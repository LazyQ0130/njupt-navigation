/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        njupt: {
          50: '#eef7ff',
          500: '#1683d8',
          700: '#075ea8',
          950: '#073456',
        },
      },
    },
  },
  plugins: [],
}

