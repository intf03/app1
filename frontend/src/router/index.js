import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

const commonRoutes = [
    {
        path: '/login',
        name: 'login',
        meta: { title: '登录' },
        component: () => import('../components/Login.vue'),
    },
    {
        path: '/other',
        name: 'other',
        meta: { title: '单独的路由' },
        component: () => import('../views/Other.vue'),
    },
    {
        path: '/404',
        name: '404',
        meta: { title: '404' },
        component: () => import('../components/404.vue'),
    },
    { path: '/', redirect: '/home' },
]

export const asyncRoutes = {
    home: {
        path: 'home',
        name: 'home',
        meta: { title: '主页' },
        component: () => import('../views/Home.vue'),
    },
    overview: {
        path: 'overview',
        name: 'overview',
        meta: { title: '总览' },
        component: () => import('../views/Home.vue'),
    },
    lineChart: {
        path: 'line-chart',
        name: 'lineChart',
        meta: { title: '数据折线图' },
        component: () => import('../views/Home.vue'),
    },
    mailMap: {
        path: 'mail-map',
        name: 'mailMap',
        meta: { title: '邮寄分布图' },
        component: () => import('../views/Home.vue'),
    },
    wordCloud: {
        path: 'word-cloud',
        name: 'wordCloud',
        meta: { title: '词云图' },
        component: () => import('../views/Home.vue'),
    },
    salesPredict: {
        path: 'sales-predict',
        name: 'salesPredict',
        meta: { title: '销量预测' },
        component: () => import('../views/Home.vue'),
    },
    dataSource: {
        path: 'data-source',
        name: 'dataSource',
        meta: { title: '数据来源' },
        component: () => import('../views/T1.vue'),
    },
    t1: {
        path: 't1',
        name: 't1',
        meta: { title: '表格' },
        component: () => import('../views/T1.vue'),
    },
    password: {
        path: 'password',
        name: 'password',
        meta: { title: '修改密码' },
        component: () => import('../views/Password.vue'),
    },
    msg: {
        path: 'msg',
        name: 'msg',
        meta: { title: '通知消息' },
        component: () => import('../views/Msg.vue'),
    },
    userinfo: {
        path: 'userinfo',
        name: 'userinfo',
        meta: { title: '用户信息' },
        component: () => import('../views/UserInfo.vue'),
    },
}

const createRouter = () => new Router({
    routes: commonRoutes,
})

const router = createRouter()

export function resetRouter() {
    const newRouter = createRouter()
    router.matcher = newRouter.matcher
}

export default router
