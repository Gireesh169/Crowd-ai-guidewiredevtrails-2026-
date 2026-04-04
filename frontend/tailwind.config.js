/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        glow: '0 0 0 1px rgba(255,255,255,0.08), 0 20px 60px rgba(0,0,0,0.45)',
      },
      keyframes: {
        softPulse: {
          '0%, 100%': { opacity: '0.72', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.02)' },
        },
        drift: {
          '0%, 100%': { transform: 'translate3d(0, 0, 0)' },
          '50%': { transform: 'translate3d(0, -10px, 0)' },
        },
      },
      animation: {
        softPulse: 'softPulse 2.6s ease-in-out infinite',
        drift: 'drift 8s ease-in-out infinite',
      },
      colors: {
        midnight: {
          950: '#050816',
          900: '#091122',
          800: '#121a2f',
        },
      },
    },
  },
  plugins: [],
};
