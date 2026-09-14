/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: '#022C22',
        primary: {
          DEFAULT: '#064E3B', // Deep Emerald
          dark: '#003527',
          forest: '#022C22',
          light: '#80bea6',
          container: '#0b513d',
          fixed: '#b0f0d6',
        },
        solar: {
          DEFAULT: '#FBBF24', // Solar Gold
          glow: '#FDE68A',
          dark: '#795900',
          container: '#ffc329',
          light: '#FFFBEB',
        },
        surface: {
          DEFAULT: '#F8FAF6',
          dim: '#D8DBD7',
          card: '#FFFFFF',
          border: '#E2E8F0',
          muted: '#F1F5F9',
        },
        eco: {
          DEFAULT: '#10B981',
          light: '#D1FAE5',
          dark: '#047857',
        },
        slateText: {
          DEFAULT: '#1E293B',
          muted: '#64748B',
          light: '#94A3B8',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
        heading: ['Plus Jakarta Sans', 'sans-serif'],
        inter: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'ambient': '0 10px 30px -5px rgba(6, 78, 59, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.02)',
        'glass': '0 8px 32px 0 rgba(6, 78, 59, 0.06)',
        'solar-glow': '0 0 25px rgba(251, 191, 36, 0.35)',
        'emerald-glow': '0 0 25px rgba(6, 78, 59, 0.25)',
      },
      backdropBlur: {
        glass: '12px',
      }
    },
  },
  plugins: [],
}
