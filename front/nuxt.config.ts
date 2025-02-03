// https://nuxt.com/docs/api/configuration/nuxt-config
export default {
    ssr: false,
    modules: [
        '@nuxtjs/color-mode',
        '@nuxt/image',
    ],
    css: [
        '~/assets/css/app.css'
    ],
    colorMode: {
        preference: 'system', // default value of $colorMode.preference
        fallback: 'dark', // fallback value if not system preference found
        hid: 'nuxt-color-mode-script',
        globalName: '__NUXT_COLOR_MODE__',
        componentName: 'ColorScheme',
        classPrefix: '',
        classSuffix: '',
        storageKey: 'nuxt-color-mode'
    },
    postcss: {
        plugins: {
            tailwindcss: {},
            autoprefixer: {}
        }
    },
    vite: {
        server: {
            fs: {
                // Allow serving files from one level up to the project root
                allow: ['/'],
            },
        },
    },
    buildModules: [
        '@nuxtjs/pwa',
    ],
    pwa: {
        manifest: {
            name: 'Onson Mail',
            short_name: 'Onson Mail',
            lang: 'ru',
            description: 'Onson Mail Group',
        },
        icon: {
            source: '/logo.png',
            fileName: 'logo.png',
        },
        meta: {
            mobileAppIOS: true
        }
    }
}
