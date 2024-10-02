module.exports = {
    content: [
      "./src/**/*.{js,jsx,ts,tsx}",
    ],
    theme: {
      extend: {
        colors: {
          'durian-light': '#FFFBDA',
          'durian-medium': '#FFEC9E',
          'durian-dark': '#FFBB70',
          'durian-accent': '#ED9455',
        },
        boxShadow: {
          'inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
        },
        scale: {
          '105': '1.05',
        },
      },
    },
    plugins: [],
  }