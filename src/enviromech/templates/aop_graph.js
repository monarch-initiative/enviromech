// Draws the pathway graph from the JSON aop_graph.py embeds: three columns, Key
// Events, dismech nodes, dismech models, joined by the links the records hold.
// No dependencies. Text from the records is set with textContent, never as HTML.
(function () {
  "use strict";
  var data = JSON.parse(document.getElementById("pathway-data").textContent);
  var figure = document.getElementById("pathway-figure");
  var details = document.getElementById("pathway-details");
  var toggle = document.getElementById("pathway-models");
  var SVG = "http://www.w3.org/2000/svg";
  var BOX = { ke: 215, node: 225, model: 215 };
  var GAPS = [165, 125], GAP_Y = 14, PAD = 12, LINE = 17, CHAR = 7.2;
  var pinned = null;

  var byId = {};
  data.key_events.forEach(function (d) { d.kind = "ke"; byId[d.id] = d; });
  data.nodes.forEach(function (d) { d.kind = "node"; byId[d.id] = d; });
  data.models.forEach(function (d) { d.kind = "model"; byId[d.id] = d; });
  var links = data.ke_node.map(function (l) { return { a: l.source, b: l.target, label: l.relation, kind: "ke-node" }; })
    .concat(data.node_model.map(function (l) { return { a: l.source, b: l.target, label: l.relationship, kind: "node-model" }; }));

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

  function subtitle(d) {
    if (d.kind === "ke") {
      var bits = [d.role ? d.role + " " + d.number : "KE " + d.number];
      if (d.level) bits.push(d.level);
      if (!d.has_record) bits.push("no record");
      else if (!d.relation) bits.push("no dismech node");
      return bits.join(" · ");
    }
    if (d.kind === "node") return [d.level, d.has_models ? "" : "no linked model"].filter(Boolean).join(" · ");
    var rels = links.filter(function (l) { return l.b === d.id && l.label; })
      .map(function (l) { return l.label.replace(/_/g, " ").toLowerCase(); })
      .filter(function (r, i, all) { return all.indexOf(r) === i; });
    return [d.section].concat(rels).filter(Boolean).join(" · ");
  }

  function isGap(d) {
    return (d.kind === "ke" && !d.relation) || (d.kind === "node" && !d.has_models);
  }

  // Connected set: from a Key Event downstream, from a model upstream, from a node both ways.
  function chain(id) {
    var seen = {}; seen[id] = true;
    function walk(from, down) {
      links.forEach(function (l) {
        var next = down ? (l.a === from ? l.b : null) : (l.b === from ? l.a : null);
        if (next && !seen[next]) { seen[next] = true; walk(next, down); }
      });
    }
    var kind = byId[id].kind;
    if (kind !== "model") walk(id, true);
    if (kind !== "ke") walk(id, false);
    return seen;
  }

  function layout(showModels) {
    var cols = [data.key_events, data.nodes].concat(showModels ? [data.models] : []);
    var kinds = ["ke", "node", "model"], x = 0, pos = {};
    cols.forEach(function (items, c) {
      var w = BOX[kinds[c]], bottom = 0;
      items.forEach(function (d) {
        var lines = wrap(d.label, w);
        d.lines = lines;
        d.sub = subtitle(d) ? wrap(subtitle(d), w, 6.6) : [];
        d.h = PAD * 2 + LINE * (lines.length + d.sub.length);
        d.w = w;
        if (c === 0) { d.target = bottom; }
        else {
          var ups = links.filter(function (l) { return l.b === d.id && pos[l.a]; })
            .map(function (l) { return pos[l.a].y + pos[l.a].h / 2; });
          d.target = ups.length ? ups.reduce(function (s, v) { return s + v; }, 0) / ups.length - d.h / 2 : bottom;
        }
      });
      items.slice().sort(function (p, q) { return p.target - q.target; }).forEach(function (d) {
        var y = Math.max(d.target, bottom);
        pos[d.id] = { x: x, y: y, w: d.w, h: d.h };
        bottom = y + d.h + GAP_Y;
      });
      x += w + (GAPS[c] || 0);
    });
    var height = Object.keys(pos).reduce(function (m, k) { return Math.max(m, pos[k].y + pos[k].h); }, 0);
    var width = Object.keys(pos).reduce(function (m, k) { return Math.max(m, pos[k].x + pos[k].w); }, 0);
    return { pos: pos, width: width, height: height };
  }

  function draw() {
    var showModels = toggle.checked;
    var L = layout(showModels), pos = L.pos;
    figure.textContent = "";
    var svg = el("svg", { viewBox: "-2 -2 " + (L.width + 4) + " " + (L.height + 4),
      width: L.width + 4, height: L.height + 4, class: "pathway-svg" }, figure);
    var edgeLayer = el("g", { class: "g-edges" }, svg);
    var labelled = {};
    links.forEach(function (l) {
      var a = pos[l.a], b = pos[l.b];
      if (!a || !b) return;
      var x1 = a.x + a.w, y1 = a.y + a.h / 2, x2 = b.x, y2 = b.y + b.h / 2, mx = (x1 + x2) / 2;
      var g = el("g", { class: "g-edge g-" + l.kind, "data-a": l.a, "data-b": l.b }, edgeLayer);
      el("path", { d: "M" + x1 + "," + y1 + " C" + mx + "," + y1 + " " + mx + "," + y2 + " " + x2 + "," + y2 }, g);
      // A Key Event's relation holds for all its nodes, so it is labelled once, where
      // its lines leave the box. A model's relationship is shown in the model's box.
      if (l.kind === "ke-node" && l.label && !labelled[l.a]) {
        labelled[l.a] = true;
        var t = el("text", { x: x1 + 6, y: y1 - 6, class: "g-edge-label" }, g);
        t.textContent = l.label.replace(/_/g, " ");
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
    highlight(pinned);
  }

  function highlight(id) {
    var on = id ? chain(id) : null;
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

  function select(id) {
    pinned = pinned === id ? null : id;
    highlight(pinned);
    details.textContent = "";
    if (!pinned) {
      para(details, "", "Select a Key Event, node or model to see what links it.");
      return;
    }
    var d = byId[pinned], h = document.createElement("h3");
    h.className = "card-title"; h.textContent = d.label; details.appendChild(h);
    para(details, "", subtitle(d));
    if (d.kind === "ke") {
      para(details, "Relation to its dismech nodes", d.relation ? d.relation.replace(/_/g, " ") : "none: no dismech node is aggregated");
      para(details, "Rationale", d.rationale);
      anchor(details, d.href, "Key Event record");
    } else if (d.kind === "node") {
      var kes = links.filter(function (l) { return l.b === d.id && l.kind === "ke-node"; })
        .map(function (l) { return byId[l.a].label + " (" + l.label.replace(/_/g, " ") + ")"; });
      para(details, "Aggregated into", kes.join("; "));
      para(details, "dismech entry", d.entry);
      para(details, "Notes", d.notes);
      anchor(details, d.href, "dismech entry page");
    } else {
      var ns = links.filter(function (l) { return l.b === d.id; })
        .map(function (l) { return byId[l.a].label + " (" + l.label.toLowerCase() + ")"; });
      para(details, "Linked to", ns.join("; "));
      para(details, "dismech reference", d.ref);
      anchor(details, d.href, "dismech entry page");
    }
  }

  toggle.addEventListener("change", function () {
    if (pinned && byId[pinned].kind === "model" && !toggle.checked) select(null);
    draw();
  });
  draw();
})();
