<script lang="ts" setup>
const navIsOpen = useState('navIsOpen', () => false)


function toggleNav(event: MouseEvent): void {
    event.preventDefault()
    navIsOpen.value = !navIsOpen.value
}

const navLinks = [
    {
        text: "Наши услуги",
        href: "/#services"
    },
    {
        text: "О нас",
        href: "/#about"
    },
    {
        text: "Отслежовать посылку",
        href: "/#tracker"
    },
    {
        text: "Наши достижения",
        href: "/#records"
    }
    
]

</script>
<template>
    <header class="inset-x-0 top-0 py-3 z-50 header">
        <AtomsContainer class-name="relative">
            <nav class="flex items-center justify-between w-full relative">
                <!-- app logo -->
                <div class="inline-flex relative bg-inherit">
                    <NuxtLink to="/" class=" flex items-center gap-2">
                        <span class="flex">
                            <img src="/logo.png" width="50" height="50" />
                        </span>
                        <span class="text-lg text-gray-700 dark:text-white">
                            <p class="mb-0 font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a]" style="line-height: 16px;">ONSON</p>
                            <p class="mb=0 font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a]" style="font-size: 12px; line-height: 12px;">MAIL TOUR</p>
                        </span>
                    </NuxtLink>
                </div>
                <div 
                    class="absolute top-full px-5 sm:px-8 md:px-12 lg:px-0 
                    lg:pt-0 lg:top-0 invisible opacity-40 lg:opacity-100 bg-body rounded-xl border border-box-border shadow-lg shadow-box-shadow 
                    lg:border-none lg:shadow-none lg:rounded-none
                    lg:bg-transparent w-full lg:w-max py-6 lg:py-0 lg:visible lg:relative flex 
                    transition-all duration-300 ease-linear origin-top translate-y-6 lg:translate-y-0"
                    :class="navIsOpen?'!visible !opacity-100 !translate-y-0':''">
                    <ul class="text-gray-700 dark:text-gray-100 w-full flex lg:items-center gap-y-4 lg:gap-x-8 flex-col lg:flex-row">
                        <AtomsNavLink v-for="navItem in navLinks" :href="navItem.href" :text="navItem.text" />
                    </ul>
                </div>

                <div class="flex items-center bg-inherit gap-1 lg:gap-3 min-w-max">
                    <ElementsThemeSwitcher />
                    <NuxtLink target="_blank" to="https://t.me/onson_mail_bot" class="transition hover:!text-primary">
                        <img src="/Telegram.svg" height="25" width="25"/>
                    </NuxtLink>

                    <NuxtLink target="_blank" to="https://www.instagram.com/onson.mail" class="transition hover:!text-primary">
                        <img class="p-2.5" src="/Instagram.svg" height="45" width="45"/>
                    </NuxtLink>

                    <div class="flex lg:hidden border-l border-box-border pl-2">
                        <button @click="toggleNav" class="outline-none w-7 h-auto flex flex-col relative">
                            <span
                                class="w-6 h-0.5 rounded-full bg-gray-500 dark:bg-gray-200 transition-all duration-300 ease-linear"
                                :class="navIsOpen ? 'translate-y-1.5 rotate-[40deg] scale-x-100 ' : ' scale-x-50 origin-left'"></span>
                            <span
                                class="w-6 origin-center  mt-1 h-0.5 rounded-full bg-gray-500 dark:bg-gray-200 transition-all duration-300 ease-linear"
                                :class="navIsOpen ? 'scale-x-0 opacity-0' : ''"></span>
                            <span
                                class="w-6 mt-1 h-0.5 rounded-full bg-gray-500 dark:bg-gray-200 transition-all duration-300 ease-linear"
                                :class="navIsOpen ? '-translate-y-1.5 -rotate-[40deg] scale-x-100 ' : ' scale-x-75 origin-left'"></span>
                        </button>
                    </div>
                </div>
            </nav>
        </AtomsContainer>
    </header>
</template>
<style>
.header {
    position: sticky;
    background-color: rgb(var(--color-bg));
}
</style>