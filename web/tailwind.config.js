module.exports = {
  purge: [
      "templates/*.html"
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {
      backgroundColor: ['checked'],
      borderColor: ['checked'],
    }
  },
  plugins: [
      require('@tailwindcss/forms')
  ],
}
