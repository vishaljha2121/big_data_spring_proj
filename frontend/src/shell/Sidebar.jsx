import React from "react";
import { NAV_GROUPS } from "./navigation.js";

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="tennis-crest" aria-hidden="true">C</div>
        <h1>Centre Court</h1>
        <p>Analytics</p>
      </div>
      <nav className="sidebar-nav" aria-label="Product navigation">
        {NAV_GROUPS.map((group) => (
          <section key={group.title} className="nav-group">
            <h2>{group.title}</h2>
            {group.items.map((item) => (
              <button
                key={item}
                type="button"
                className={activePage === item ? "active" : ""}
                onClick={() => onNavigate(item)}
              >
                <span>{activePage === item ? "●" : "○"}</span>
                {item}
              </button>
            ))}
          </section>
        ))}
      </nav>
      <div className="sidebar-footer">
        <span>Project mode</span>
        <strong>Historical tennis + ML + replay</strong>
      </div>
    </aside>
  );
}
