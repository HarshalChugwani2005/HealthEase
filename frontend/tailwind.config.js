/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Hospital Theme
                hospital: {
                    primary: '#1C6DD0',    // Medical Blue
                    secondary: '#00B8A9',  // Teal
                    alert: '#E63946',      // Alert Red
                    success: '#2A9D8F',    // Success Green
                    bg: '#F7F9FC'          // Soft White
                },
                // Patient Theme
                patient: {
                    primary: '#6C63FF',    // Soft Purple
                    secondary: '#48CAE4',  // Sky Blue
                    accent: '#C0F500',     // Lime
                    bg: '#F8F7FF'          // Light Lavender
                },
                // Admin Theme
                admin: {
                    primary: '#14213D',    // Deep Navy
                    accent: '#FCA311',     // Gold
                    bg: '#F5F5F5'          // Background Grey
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
