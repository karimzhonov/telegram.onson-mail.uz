<script setup lang="ts">
useHead({
  title: 'Onson Mail Tour',
  meta: [
    { name: 'description', content: 'Cargo, turism and consalting' },
  ],
  link: [
    { rel: 'icon', type: 'image/png', href: '/logo.png' }
  ],
})
</script>
<template>
    <div>
        <SectionsHomeHeroSection/>
        <SectionsHomeLatestPodcast/>
        <!-- <SectionsHomePopularPodcasts/> -->
        <SectionsAboutPodux/>
        <SectionsCallToAction/>
        <SectionsWhyUs/>
    </div>
</template>