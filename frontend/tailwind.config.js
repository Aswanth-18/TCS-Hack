/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        sage: {
          50: '#f6f8f6',
          100: '#eaf0eb',
          200: '#d4e1d6',
          300: '#b2cbb5',
          400: '#8cae90',
          500: '#67906c',
          600: '#517455',
          700: '#415c44',
          800: '#364a38',
          900: '#2c3c2e',
        },
        surface: {
          ground: '#fbfbf9',
          card: '#ffffff',
          muted: '#f4f5f1',
          border: '#e6e9e3',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      boxShadow: {
        subtle: '0 1px 3px 0 rgba(0, 0, 0, 0.04), 0 1px 2px -1px rgba(0, 0, 0, 0.04)',
        card: '0 4px 6px -1px rgba(22, 101, 52, 0.04), 0 2px 4px -2px rgba(22, 101, 52, 0.04)',
        elevated: '0 10px 15px -3px rgba(22, 101, 52, 0.06), 0 4px 6px -4px rgba(22, 101, 52, 0.06)',
      }
    },
  },
  plugins: [],
}

