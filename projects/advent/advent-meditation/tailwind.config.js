/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        advent: {
          primary: '#2E1065', // Deep Purple
          accent: '#F59E0B',  // Gold
          bg: '#0F172A',      // Very Dark Blue/Black
          text: '#F8FAFC',    // Off-white/Cream
          muted: '#94A3B8',   // Slate 400
        }
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'serif'],
        sans: ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'stars': "url('/stars.png')", // Placeholder, will use CSS or SVG later
      }
    },
  },
  plugins: [],
}
