import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#427F8C", // dark teal
          50: "#f0f9fa",
          100: "#d9f0f3",
          200: "#b7e2e8",
          300: "#8bcdd7",
          400: "#58b0c0",
          500: "#427F8C", // main color
          600: "#3a6f7a",
          700: "#325c66",
          800: "#2d4d55",
          900: "#294149",
        },
        secondary: {
          DEFAULT: "#73B1BF", // medium teal
          50: "#f2f9fb",
          100: "#e0f1f5",
          200: "#c5e4ec",
          300: "#9dd1de",
          400: "#73B1BF", // main color
          500: "#5a9aab",
          600: "#4d8192",
          700: "#426a77",
          800: "#3b5862",
          900: "#344a53",
        },
        accent: {
          DEFAULT: "#CECF2", // light blue/cyan
          50: "#f0fffe",
          100: "#CECF2", // main color
          200: "#b8f2f1",
          300: "#7ee8e6",
          400: "#3dd5d2",
          500: "#23bfbc",
          600: "#1e9a98",
          700: "#1f7a79",
          800: "#1f6162",
          900: "#1e5152",
        },
        background: {
          DEFAULT: "#F2F2F2", // light gray
        },
        text: {
          DEFAULT: "#0D0D0D", // black
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui"],
      },
    },
  },
  plugins: [],
};

export default config;
