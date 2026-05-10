import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

const store = new Vuex.Store({
    state: {
        isShowLoading: false,
        menuItems: [
            {
                name: 'home',
                size: 18,
                type: 'md-home',
                text: '主页',
            },
            {
                name: 'overview',
                size: 18,
                type: 'ios-grid',
                text: '总览',
            },
            {
                name: 'lineChart',
                size: 18,
                type: 'ios-analytics-outline',
                text: '数据折线图',
            },
            {
                name: 'mailMap',
                size: 18,
                type: 'ios-map-outline',
                text: '邮寄分布图',
            },
            {
                name: 'wordCloud',
                size: 18,
                type: 'ios-cloud-outline',
                text: '词云图',
            },
            {
                name: 'salesPredict',
                size: 18,
                type: 'ios-trending-up',
                text: '销量预测',
            },
            {
                name: 'dataSource',
                size: 18,
                type: 'md-arrow-forward',
                text: '数据来源',
            },
        ],
    },
    mutations: {
        setMenus(state, items) {
            state.menuItems = [...items]
        },
        setLoading(state, isShowLoading) {
            state.isShowLoading = isShowLoading
        },
    },
})

export default store
