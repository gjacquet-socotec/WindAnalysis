/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Identité visuelle du projet (bleu SOCOTEC/Wind)
        primary: {
          dark: '#2F5597',   // Bleu foncé pour en-têtes
          light: '#D9E1F2',  // Bleu clair pour lignes alternées
        },
      },
    },
  },
  plugins: [],
}
