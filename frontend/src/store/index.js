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
                size: 18,
                type: 'ios-cloud-outline',
                text: '词云图',
                children: [
                    {
                        name: 'productWordCloud',
                        size: 18,
                        type: 'ios-leaf',
                        text: '商品词云图',
                    },
                    {
                        name: 'addressWordCloud',
                        size: 18,
                        type: 'ios-heart-outline',
                        text: '地址词云图',
                    },
                ],
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
            {
                name: 'password',
                size: 18,
                type: 'md-lock',
                text: '修改密码',
                hidden: true,
            },
            {
                name: 'userinfo',
                size: 18,
                type: 'md-person',
                text: '基本资料',
                hidden: true,
            },
            {
                name: 'msg',
                size: 18,
                type: 'ios-notifications-outline',
                text: '通知消息',
                hidden: true,
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
