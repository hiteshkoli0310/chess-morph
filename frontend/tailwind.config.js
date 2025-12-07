/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        dessert: {
          vanilla: "#FFF8E1",
          chocolate: "#3E2723",
          milkChoc: "#8D6E63",
          mint: "#4DB6AC",
          caramel: "#FFB74D",
          strawberry: "#D81B60",
          dark: "#1a1a1a",
          text: "#3E2723",
        },
      },
      fontFamily: {
        sans: ['"Segoe UI"', "Tahoma", "Geneva", "Verdana", "sans-serif"],
      },
    },
  },
  plugins: [],
};
