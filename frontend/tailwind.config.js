/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,jsx}'],
    theme: {
        extend: {
            boxShadow: {
                soft: '0 25px 60px -25px rgba(15, 23, 42, 0.45)',
            },
        },
    },
    plugins: [],
}
