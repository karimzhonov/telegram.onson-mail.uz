<template>
    <section class="pt-20" id="tracker">
        <AtomsContainer>
            <div
                class="w-full relative py-8 md:py-10 px-6 md:px-8 rounded-2xl bg-gradient-to-tr from-gray-100 to-gray-200 dark:from-gray-900 dark:to-body-color">
                <div class="absolute right-0 top-0 h-full w-full flex justify-end">
                    <span class="flex opacity-20">
                        <span class="w-16 h-32 rounded-l-full flex bg-primary blur-2xl"></span>
                        <span class="w-16 h-32 rounded-r-full flex bg-[#f88fc2] blur-2xl mt-14"></span>
                    </span>
                </div>

                <div class="absolute left-0 bottom-0 h-full w-full flex items-end">
                    <span class="flex opacity-20">
                        <span class="w-16 h-32 rounded-l-full flex bg-primary blur-2xl"></span>
                        <span class="w-16 h-32 rounded-r-full flex bg-[#f88fc2] blur-2xl mt-14"></span>
                    </span>
                </div>
                <div class="mx-auto text-center max-w-xl md:max-w-2xl relative">
                    <h2 class="text-gray-800 pt-4 dark:text-white font-bold text-4xl md:text-5xl lg:text-6x">
                        Отслеживайте свою  
                        <span class="text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a]">посылку</span>
                    </h2>
                    <p class="text-gray-600 dark:text-gray-300 pt-8 mx-auto max-w-xl">
                        Отслеживайте статус и местоположение вашей посылки в режиме реального времени. Введите номер отслеживания и получите актуальную информацию о перемещении вашего заказа. Быстро, удобно и надежно!
                    </p>
                    <div class="mx-auto max-w-md sm:max-w-xl pt-10">
                        <div class="flex items-center relative gap-x-2">
                            <input v-model="number" type="text" placeholder="Введите номер отслеживания" @keydown.enter="fetch_order"
                                class="outline-none border-2 border-transparent focus:border-primary bg-body text-gray-600 dark:text-gray-200 rounded-3xl px-6 py-3 w-full">
                            <div
                                class="sm:inline-flex sm:min-w-max absolute sm:relative top-0.5 right-0.5 sm:top-0 sm:right-0">
                                <button class="min-w-max p-3 sm:py-3 sm:px-6 text-white border-2 border-transparent relative group" @click="fetch_order">
                                    <span
                                        class="absolute inset-0 rounded-full group-hover:scale-105 origin-center transition-all ease-in-out bg-primary"></span>
                                    <span aria-hidden="true" class="relative hidden sm:flex">
                                        Отслеживать
                                    </span>
                                    <span class="relative flex sm:hidden">
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                            stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                                            <path stroke-linecap="round" stroke-linejoin="round"
                                                d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
                                        </svg>
                                    </span>
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="mx-auto max-w-md sm:max-w-xl mt-10 text-start" v-if="order">
                        <div class="flex mb-2">    
                            <p class="text-gray-600 dark:text-gray-300 text-xl" style="text-wrap: nowrap">Hомер отслеживания: </p>
                            <p class="font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a] ml-2 text-xl" style="text-wrap: nowrap">{{ order.number }}</p>
                        </div>
                        <div class="flex mb-2">    
                            <p class="text-gray-600 dark:text-gray-300 text-xl" style="text-wrap: nowrap">Текущее состояние:</p>
                            <p class="font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a] ml-2 text-xl" style="text-wrap: nowrap">{{ order.part.status }} </p>
                        </div>

                        <div class="flex mb-2">    
                            <p class="text-gray-600 dark:text-gray-300 text-xl" style="text-wrap: nowrap">Партия:</p>
                            <p class="font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a] ml-2 text-xl" style="text-wrap: nowrap">{{ order.part.number }} </p>
                        </div>

                        <div class="flex mb-2">    
                            <p class="text-gray-600 dark:text-gray-300 text-xl" style="text-wrap: nowrap">Филиал:</p>
                            <p class="font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a] ml-2 text-xl" style="text-wrap: nowrap">{{ order.part.storage }} </p>
                        </div>
                        
                        <div class="flex mb-2">    
                            <p class="text-gray-600 dark:text-gray-300 text-xl flex" style="text-wrap: nowrap">Название тавара: <p class="font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a] ml-2 text-xl" lang="ru" style="word-wrap: break-word;hyphens: auto;">{{ order.name }} </p></p>
                        </div>

                        <div class="flex mb-2">    
                            <p class="text-gray-600 dark:text-gray-300 text-xl" style="text-wrap: nowrap">Клиент ИД:</p>
                            <p class="font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a] ml-2 text-xl" style="text-wrap: nowrap">{{ order.clientid }} </p>
                        </div>
                        <div class="flex mb-2">    
                            <p class="text-gray-600 dark:text-gray-300 text-xl" style="text-wrap: nowrap">Дата:</p>
                            <p class="font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a] ml-2 text-xl" style="text-wrap: nowrap">{{ order.date }} </p>
                        </div>
                    </div>
                    <div class="mx-auto max-w-md sm:max-w-xl mt-10" v-if="error">
                        <p class="font-bold text-transparent bg-clip-text bg-gradient-to-br from-primary to-[#8cd66a]">Заказ не найден. Пожалуйста, проверьте введённые номер отслеживание или попробуйте позже</p>
                    </div>
                </div>
            </div>
        </AtomsContainer>
    </section>
</template>
<script>
import axios from 'axios';
export default {
    name: 'Action',
    data() {
        return {
            number: null,
            order: null,
            error: false
        }
    },
    methods: {
        async fetch_order() {
            this.error = false
            if (!this.number) return
            try {
                // const response = await axios.get(`http://localhost:8000/api/orders/order/${this.number}/`)
                const response = await axios.get(`https://api.onson-mail.uz/api/orders/order/${this.number}/`)
                this.order = response.data
            } catch {
                this.error = true
            }
            
        }
    }
}
</script>