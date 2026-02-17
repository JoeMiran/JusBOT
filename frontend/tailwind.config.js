/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Adicionando um dourado personalizado para o JusAI
        'jus-gold': '#d4af37', 
        'jus-dark': '#0f172a',
      }
    },
  },
  plugins: [],
}