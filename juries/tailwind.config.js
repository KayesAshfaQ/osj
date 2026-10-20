/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./lib/**/*.dart",
    "./web/**/*.html"
  ],
  theme: {
    extend: {
      colors: {
        juris: {
          dark: '#005049',
          main: '#00685f',
          light: '#d3e4fe',
          bg: '#f8f9ff',
          text: '#0b1c30',
          gray: '#3d4947'
        }
      }
    },
  },
  plugins: [],
}
