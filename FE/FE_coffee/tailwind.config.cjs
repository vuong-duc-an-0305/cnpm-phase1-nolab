module.exports = {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx,html}'],
  theme: {
    extend: {
      colors: {
        coffee: {
          50: '#F5F5DC',
          100: '#FFF8E1',
          200: '#F5DEB3',
          300: '#D4AF37',
          400: '#B8860B',
          500: '#4B2E2E',
          600: '#3E2723',
          700: '#2C1E1A',
          800: '#1A120F',
          900: '#0F0A08',
        },
      },
      fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui'] },
      // giữ keyframes/animation nếu cần
    },
  },
  plugins: [],
}
