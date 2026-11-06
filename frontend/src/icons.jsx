// Authored icon set — single 1.5 stroke, currentColor.
const base = {
  width: 16,
  height: 16,
  viewBox: "0 0 16 16",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.5,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

export const Plus = (p) => (
  <svg {...base} {...p}>
    <path d="M8 3.5v9M3.5 8h9" />
  </svg>
);

export const Send = (p) => (
  <svg {...base} {...p}>
    <path d="M8 13V3.5M4.5 7 8 3.5 11.5 7" />
  </svg>
);

export const Doc = (p) => (
  <svg {...base} {...p}>
    <path d="M4 2.5h5l3 3V13a.5.5 0 0 1-.5.5h-7A.5.5 0 0 1 4 13V3a.5.5 0 0 1 .5-.5Z" />
    <path d="M9 2.5V5.5h3" />
  </svg>
);

export const Trash = (p) => (
  <svg {...base} {...p}>
    <path d="M3.5 4.5h9M6.5 4.5V3.5a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 .5.5v1M5 4.5l.5 8a.5.5 0 0 0 .5.5h4a.5.5 0 0 0 .5-.5l.5-8" />
  </svg>
);

export const Upload = (p) => (
  <svg {...base} {...p}>
    <path d="M8 10.5V3.5M5 6l3-3 3 3M3.5 12.5h9" />
  </svg>
);

export const Close = (p) => (
  <svg {...base} {...p}>
    <path d="M4 4l8 8M12 4l-8 8" />
  </svg>
);

// Citadel mark — an enclosed keep.
export const Mark = (p) => (
  <svg {...base} {...p} viewBox="0 0 20 20">
    <path d="M10 2.5 16.5 5v5.5c0 3.2-2.6 5.6-6.5 7-3.9-1.4-6.5-3.8-6.5-7V5L10 2.5Z" />
    <path d="M10 8.5v4M8 10.5h4" />
  </svg>
);
