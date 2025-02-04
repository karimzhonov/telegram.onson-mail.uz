// https://nuxt.com/docs/api/configuration/nuxt-config
import {defineNuxtConfig} from 'nuxt/config'

export default defineNuxtConfig({
    ssr: false,

    modules: [
        "@vite-pwa/nuxt",
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

    pwa: {
        // strategies: 'injectManifest',
        // srcDir: 'service-worker',
        // filename: 'sw.ts',
        // registerType: 'autoUpdate',
        manifest: {
            name: "Onson Mail",
            short_name: "Onson Mail",
            description: "Onson Mail Group",
            // display: "minimal-ui",
            // start_url: "/",
            // scope: "/",
            theme_color: '#00D8A5',
            icons: [
                {
                    src: "/icons/logo64.png",
                    sizes: "64x64",
                    type: "image/png",
                },
                {
                    src: "/icons/logo144.png",
                    sizes: "144x144",
                    type: "image/png",
                },
                {
                    src: "/icons/logo192.png",
                    sizes: "192x192",
                    type: "image/png",
                },
                {
                    src: '/icons/logo512.png',
                    sizes: '512x512',
                    type: 'image/png',
                },
            ],
        },
        workbox: {
            navigateFallback: '/',
        },
        // injectManifest: {
        //     globPatterns: ['**/*.{js,css,html,png,svg,ico}'],
        // },
        client: {
            installPrompt: true,
            // you don't need to include this: only for testing purposes
            // if enabling periodic sync for update use 1 hour or so (periodicSyncForUpdates: 3600)
            periodicSyncForUpdates: 20,
        },
        devOptions: {
            enabled: true,
            // suppressWarnings: true,
            // navigateFallback: '/',
            // navigateFallbackAllowlist: [/^\/$/],
            type: 'module',
        },
    },

    compatibilityDate: '2025-02-03',
})