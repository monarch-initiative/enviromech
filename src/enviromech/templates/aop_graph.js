// Draws an AOP's graph from the JSON aop_graph.py embeds, in two views:
//   Pathway: Key Events, then the dismech nodes they aggregate, then the dismech
//            models linked to those nodes.
//   Methods: Key Events; EnviroMech assays with no dismech counterpart; methods
//            that are both an EnviroMech assay and a dismech model; dismech models
//            with no EnviroMech counterpart; then the dismech nodes.
// No dependencies. Text from the records is set with textContent, never as HTML.
(function () {
  "use strict";
  var data = JSON.parse(document.getElementById("pathway-data").textContent);
  var figure = document.getElementById("pathway-figure");
  var details = document.getElementById("pathway-details");
  var toggle = document.getElementById("pathway-models");
  var modelsControl = document.getElementById("pathway-models-control");
  var SVG = "http://www.w3.org/2000/svg";
  var GAP_Y = 14, PAD = 12, LINE = 17, CHAR = 7.2, HEADER = 34;
  var view = "pathway", pinned = null;
  var EMPTY = "Select a box to see what links it.";

  // Every item, by id. A shared method is one box standing for an assay and a model.
  var byId = {};
  data.key_events.forEach(function (d) { d.kind = "ke"; byId[d.id] = d; });
  data.nodes.forEach(function (d) { d.kind = "node"; byId[d.id] = d; });
  data.models.forEach(function (d) { d.kind = "model"; byId[d.id] = d; });
  (data.assays || []).forEach(function (d) { d.kind = "assay"; byId[d.id] = d; });
  var methods = data.methods || { assays_only: [], shared: [], models_only: [] };
  var sharedOf = {};
  methods.shared.forEach(function (pair) {
    var id = "shared:" + pair.assay + "|" + pair.model;
    var assay = byId[pair.assay], model = byId[pair.model];
    byId[id] = { id: id, kind: "shared", label: assay.label, assay: assay, model: model };
    sharedOf[pair.assay] = id; sharedOf[pair.model] = id;
  });
  function methodId(id) { return sharedOf[id] || id; }

  function words(s) { return String(s || "").replace(/_/g, " ").toLowerCase(); }

  // Each view: its columns (left to right), the order to place them in, and its links.
  // A hidden link is used for highlighting and layout but not drawn.
  function buildView(name) {
    var links = [], cols;
    if (name === "pathway") {
      data.ke_node.forEach(function (l) { links.push({ a: l.source, b: l.target, label: l.relation, kind: "ke-node" }); });
      if (toggle.checked) {
        data.node_model.forEach(function (l) {
          links.push({ a: l.source, b: l.target, label: l.relationship, kind: "node-model" });
        });
      }
      cols = [
        { head: "Key Events", w: 215, ids: data.key_events.map(function (d) { return d.id; }) },
        { head: "dismech nodes", w: 225, ids: data.nodes.map(function (d) { return d.id; }) },
      ];
      if (toggle.checked) cols.push({ head: "dismech models", w: 215, ids: data.models.map(function (d) { return d.id; }) });
      return { cols: cols, order: [0, 1, 2], gaps: [165, 125], links: links };
    }
    (data.ke_assay || []).forEach(function (l) {
      links.push({ a: l.source, b: methodId(l.target), kind: "ke-assay" });
    });
    data.node_model.forEach(function (l) {
      links.push({ a: methodId(l.target), b: l.source, label: l.relationship, kind: "model-node" });
    });
    data.ke_node.forEach(function (l) { links.push({ a: l.source, b: l.target, kind: "ke-node", hidden: true }); });
    (data.assays || []).forEach(function (assay) {
      assay.same_readout.forEach(function (model) {
        if (byId[model]) links.push({ a: methodId(assay.id), b: methodId(model), label: "same readout", kind: "same-readout" });
      });
    });
    cols = [
      { head: "Key Events", w: 180, ids: data.key_events.map(function (d) { return d.id; }) },
      { head: "EnviroMech assays only", w: 180, ids: methods.assays_only },
      { head: "In both", w: 190, ids: methods.shared.map(function (p) { return sharedOf[p.assay]; }) },
      { head: "dismech models only", w: 180, ids: methods.models_only },
      { head: "dismech nodes", w: 190, ids: data.nodes.map(function (d) { return d.id; }) },
    ];
    // Nodes are placed before the dismech-only models, so those models sit by their nodes.
    return { cols: cols, order: [0, 1, 2, 4, 3], gaps: [50, 50, 70, 120], links: links };
  }

  function el(name, attrs, parent) {
    var e = document.createElementNS(SVG, name);
    Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (parent) parent.appendChild(e);
    return e;
  }

  function wrap(text, width, charWidth) {
    var max = Math.max(8, Math.floor((width - 2 * PAD) / (charWidth || CHAR))), lines = [], line = "";
    String(text).split(/\s+/).forEach(function (word) {
      if (line && (line + " " + word).length > max) { lines.push(line); line = word; }
      else { line = line ? line + " " + word : word; }
    });
    if (line) lines.push(line);
    return lines;
  }

  function subtitle(d, V) {
    if (d.kind === "ke") {
      var bits = [d.role ? d.role + " " + d.number : "KE " + d.number];
      if (d.level) bits.push(d.level);
      if (!d.has_record) bits.push("no record");
      else if (view === "pathway" && !d.relation) bits.push("no dismech node");
      else if (view === "methods" && !d.relation && !hasAssay(d.id)) bits.push("no assay or node");
      return bits.join(" · ");
    }
    if (d.kind === "node") return [d.level, d.has_models ? "" : "no linked model"].filter(Boolean).join(" · ");
    if (d.kind === "assay") return d.guidelines.join(", ") || "no test guideline";
    if (d.kind === "shared") return [d.assay.guidelines.join(", "), "also a dismech model"].filter(Boolean).join(" · ");
    // A model: its section, and in the pathway view its relationships to its nodes
    // (the methods view labels them on the lines instead).
    var rels = view !== "pathway" ? [] : V.links.filter(function (l) { return l.kind === "node-model" && l.b === d.id; })
      .map(function (l) { return words(l.label); })
      .filter(function (r, i, all) { return r && all.indexOf(r) === i; });
    return [d.section].concat(rels).filter(Boolean).join(" · ");
  }

  function hasAssay(keId) { return (data.ke_assay || []).some(function (l) { return l.source === keId; }); }

  function isGap(d) {
    if (d.kind === "ke") return view === "pathway" ? !d.relation : !d.relation && !hasAssay(d.id);
    return d.kind === "node" && !d.has_models;
  }

  function neighbours(V, id, kinds) {
    var out = [];
    V.links.forEach(function (l) {
      if (kinds && kinds.indexOf(l.kind) < 0) return;
      if (l.a === id) out.push(l.b);
      if (l.b === id) out.push(l.a);
    });
    return out;
  }

  // What lights up with a box. Pathway: from a Key Event downstream, from a model
  // upstream, from a node both ways. Methods: a Key Event with its assays and its
  // nodes' models; a method with its Key Events, by mapping or through its node.
  function chain(V, id) {
    var seen = {}; seen[id] = true;
    function add(ids) { ids.forEach(function (x) { seen[x] = true; }); return ids; }
    var kind = byId[id].kind;
    if (view === "pathway") {
      var walk = function (from, down) {
        V.links.forEach(function (l) {
          var next = down ? (l.a === from ? l.b : null) : (l.b === from ? l.a : null);
          if (next && !seen[next]) { seen[next] = true; walk(next, down); }
        });
      };
      if (kind !== "model") walk(id, true);
      if (kind !== "ke") walk(id, false);
      return seen;
    }
    if (kind === "ke") {
      add(neighbours(V, id, ["ke-assay"]));
      add(neighbours(V, id, ["ke-node"])).forEach(function (n) { add(neighbours(V, n, ["model-node"])); });
    } else if (kind === "node") {
      add(neighbours(V, id, ["ke-node", "model-node"]));
    } else {
      add(neighbours(V, id, ["ke-assay", "same-readout"]));
      add(neighbours(V, id, ["model-node"])).forEach(function (n) { add(neighbours(V, n, ["ke-node"])); });
    }
    return seen;
  }

  function layout(V) {
    var pos = {}, xs = [], x = 0;
    V.cols.forEach(function (col, c) { xs.push(x); x += col.w + (V.gaps[c] || 0); });
    V.order.forEach(function (c) {
      var col = V.cols[c];
      if (!col) return;
      var bottom = HEADER, items = col.ids.map(function (id) { return byId[id]; });
      items.forEach(function (d) {
        d.lines = wrap(d.label, col.w);
        var sub = subtitle(d, V);
        d.sub = sub ? wrap(sub, col.w, 6.6) : [];
        d.h = PAD * 2 + LINE * (d.lines.length + d.sub.length);
        d.w = col.w;
        var placed = neighbours(V, d.id).filter(function (n) { return pos[n]; })
          .map(function (n) { return pos[n].y + pos[n].h / 2; });
        d.target = c === V.order[0] || !placed.length ? null
          : placed.reduce(function (s, v) { return s + v; }, 0) / placed.length - d.h / 2;
      });
      var ordered = items.slice();
      if (c !== V.order[0]) {
        ordered.sort(function (p, q) {
          return (p.target === null ? 1e9 : p.target) - (q.target === null ? 1e9 : q.target);
        });
      }
      ordered.forEach(function (d) {
        var y = Math.max(d.target === null ? bottom : d.target, bottom);
        pos[d.id] = { x: xs[c], y: y, w: d.w, h: d.h };
        bottom = y + d.h + GAP_Y;
      });
    });
    var height = Object.keys(pos).reduce(function (m, k) { return Math.max(m, pos[k].y + pos[k].h); }, HEADER);
    return { pos: pos, xs: xs, width: x - (V.gaps[V.cols.length - 1] || 0), height: height };
  }

  var current = null;

  function draw() {
    var V = buildView(view), L = layout(V), pos = L.pos;
    current = V;
    figure.textContent = "";
    var svg = el("svg", { viewBox: "-2 -2 " + (L.width + 4) + " " + (L.height + 4),
      width: L.width + 4, height: L.height + 4, class: "pathway-svg pathway-" + view }, figure);
    V.cols.forEach(function (col, c) {
      var t = el("text", { x: L.xs[c], y: 16, class: "g-head" }, svg);
      t.textContent = col.head + " (" + col.ids.length + ")";
    });
    var edgeLayer = el("g", { class: "g-edges" }, svg);
    var labelled = {};
    V.links.forEach(function (l) {
      var a = pos[l.a], b = pos[l.b];
      if (!a || !b || l.hidden) return;
      var left = a.x <= b.x ? a : b, right = a.x <= b.x ? b : a;
      var x1 = left.x + left.w, y1 = left.y + left.h / 2, x2 = right.x, y2 = right.y + right.h / 2;
      var mx = (x1 + x2) / 2;
      var g = el("g", { class: "g-edge g-" + l.kind, "data-a": l.a, "data-b": l.b }, edgeLayer);
      el("path", { d: "M" + x1 + "," + y1 + " C" + mx + "," + y1 + " " + mx + "," + y2 + " " + x2 + "," + y2 }, g);
      // A Key Event's relation holds for all its nodes, so it is labelled once, where
      // its lines leave the box. A model's relationship is shown in its box, or on the
      // line to its node in the methods view.
      var text = null, tx = x1 + 6, ty = y1 - 6;
      if (l.kind === "ke-node" && l.label && !labelled[l.a]) { labelled[l.a] = true; text = words(l.label); }
      if (l.kind === "model-node" && l.label) { text = words(l.label); tx = x1 + 4; ty = y1 - 5; }
      if (l.kind === "same-readout") { text = "same readout"; tx = mx - 30; ty = (y1 + y2) / 2 - 5; }
      if (text) {
        var t = el("text", { x: tx, y: ty, class: "g-edge-label" }, g);
        t.textContent = text;
      }
    });
    Object.keys(pos).forEach(function (id) {
      var d = byId[id], p = pos[id];
      var g = el("g", { class: "g-box g-" + d.kind + (isGap(d) ? " g-gap" : ""), "data-id": id,
        tabindex: "0", role: "button", transform: "translate(" + p.x + "," + p.y + ")" }, svg);
      var title = el("title", {}, g);
      title.textContent = d.label;
      el("rect", { width: p.w, height: p.h, rx: 7 }, g);
      d.lines.forEach(function (line, i) {
        var t = el("text", { x: PAD, y: PAD + LINE * (i + 0.8), class: "g-label" }, g);
        t.textContent = line;
      });
      d.sub.forEach(function (line, i) {
        var s = el("text", { x: PAD, y: PAD + LINE * (d.lines.length + i + 0.8), class: "g-sub" }, g);
        s.textContent = line;
      });
      g.addEventListener("mouseenter", function () { if (!pinned) highlight(id); });
      g.addEventListener("mouseleave", function () { if (!pinned) highlight(null); });
      g.addEventListener("focus", function () { if (!pinned) highlight(id); });
      g.addEventListener("click", function () { select(id); });
      g.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); select(id); }
        if (e.key === "Escape") select(null);
      });
    });
    if (pinned && !pos[pinned]) pinned = null;
    highlight(pinned);
  }

  function highlight(id) {
    var on = id ? chain(current, id) : null;
    figure.querySelectorAll(".g-box").forEach(function (g) {
      var k = g.getAttribute("data-id");
      g.classList.toggle("is-dim", !!on && !on[k]);
      g.classList.toggle("is-on", !!on && k === id);
    });
    figure.querySelectorAll(".g-edge").forEach(function (g) {
      g.classList.toggle("is-dim", !!on && !(on[g.getAttribute("data-a")] && on[g.getAttribute("data-b")]));
    });
  }

  function para(parent, label, text) {
    if (!text) return;
    var p = document.createElement("p");
    if (label) { var b = document.createElement("strong"); b.textContent = label + ": "; p.appendChild(b); }
    p.appendChild(document.createTextNode(text));
    parent.appendChild(p);
  }

  function anchor(parent, href, text) {
    if (!href) return;
    var p = document.createElement("p"), a = document.createElement("a");
    a.href = href; a.textContent = text; p.appendChild(a); parent.appendChild(p);
  }

  function labelsOf(ids) { return ids.map(function (x) { return byId[x] ? byId[x].label : x; }).join("; "); }

  function keysMapping(assayId) {
    return (data.ke_assay || []).filter(function (l) { return l.target === assayId; })
      .map(function (l) { return byId[l.source].label; }).join("; ");
  }

  function nodeLinks(modelId) {
    return data.node_model.filter(function (l) { return l.target === modelId; })
      .map(function (l) { return byId[l.source].label + " (" + words(l.relationship) + ")"; }).join("; ");
  }

  function select(id) {
    pinned = id && pinned !== id ? id : null;
    highlight(pinned);
    details.textContent = "";
    if (!pinned) { para(details, "", EMPTY); return; }
    var d = byId[pinned], h = document.createElement("h3");
    h.className = "card-title"; h.textContent = d.label; details.appendChild(h);
    para(details, "", subtitle(d, current));
    if (d.kind === "ke") {
      para(details, "Relation to its dismech nodes", d.relation ? words(d.relation) : "none: no dismech node is aggregated");
      var assays = (data.ke_assay || []).filter(function (l) { return l.source === d.id; }).map(function (l) { return l.target; });
      para(details, "EnviroMech assays", labelsOf(assays) || "none");
      para(details, "Rationale", d.rationale);
      anchor(details, d.href, "Key Event record");
    } else if (d.kind === "node") {
      var kes = data.ke_node.filter(function (l) { return l.target === d.id; })
        .map(function (l) { return byId[l.source].label + " (" + words(l.relation) + ")"; });
      para(details, "Aggregated into", kes.join("; "));
      para(details, "dismech entry", d.entry);
      para(details, "Notes", d.notes);
      anchor(details, d.href, "dismech entry page");
    } else if (d.kind === "assay" || d.kind === "shared") {
      var a = d.kind === "shared" ? d.assay : d;
      para(details, "Mapped to", keysMapping(a.id));
      para(details, "Mapping source", a.reference);
      para(details, "Description", a.description);
      if (d.kind === "shared") {
        para(details, "Same method as dismech model", d.model.label + " (" + d.model.ref + ")");
        para(details, "dismech node", nodeLinks(d.model.id));
        anchor(details, d.model.href, "dismech entry page");
      } else if (a.same_readout.length) {
        para(details, "Same readout, other systems, in dismech", labelsOf(a.same_readout));
      } else if (a.same_method.length) {
        para(details, "Also a dismech model, on a node no Key Event of this AOP aggregates",
          a.same_method.map(function (m) { return m.replace(/^model:/, ""); }).join("; "));
      }
    } else {
      para(details, "Linked to", nodeLinks(d.id));
      var readers = (data.assays || []).filter(function (x) { return x.same_readout.indexOf(d.id) >= 0; })
        .map(function (x) { return x.id; });
      para(details, "Same readout as EnviroMech assays", labelsOf(readers));
      para(details, "dismech reference", d.ref);
      anchor(details, d.href, "dismech entry page");
    }
  }

  toggle.addEventListener("change", function () {
    if (pinned && byId[pinned].kind === "model" && !toggle.checked) select(null);
    draw();
  });
  document.querySelectorAll('input[name="pathway-view"]').forEach(function (input) {
    input.addEventListener("change", function () {
      view = input.value;
      modelsControl.hidden = view !== "pathway";
      select(null);
      draw();
    });
  });
  draw();
})();
