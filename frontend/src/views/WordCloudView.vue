<template>
    <div class="word-cloud-page">
        <div class="section-card chart-card">
            <div class="section-title">▣ 图表</div>
            <div class="cloud-shell">
                <div class="cloud-header">▣ {{ cloudTitle }}</div>
                <div class="cloud-canvas" :class="mode">
                    <Spin v-if="loading" fix size="large" />
                    <div v-if="!loading && !cloudWords.length" class="cloud-empty">暂无词云数据</div>
                    <span
                        v-for="(item, index) in cloudWords"
                        :key="item.name + index"
                        class="cloud-word"
                        :style="getWordStyle(item)"
                        :title="item.name + '：' + item.value"
                    >
                        {{ item.name }}
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
const PRODUCT_KEYWORDS = [
    '纸巾', '抽纸', '卫生纸', '卷纸', '湿巾', '家用', '日用品', '厨房', '清洁', '洗护', '毛巾', '浴巾', '牙刷', '牙膏',
    '洗衣液', '洗发水', '沐浴露', '收纳', '垃圾袋', '保鲜膜', '一次性', '套装', '大号', '小号', '加厚', '多功能',
    '食品', '零食', '饼干', '坚果', '水果', '饮料', '咖啡', '茶叶', '蜂蜜', '面包', '牛肉', '麻辣', '锅巴', '下饭菜',
    '服装', '女装', '男装', '外套', '毛衣', '卫衣', '短袖', '长袖', '裤子', '裙子', '牛仔', '宽松', '休闲', '秋冬', '春夏',
    '办公', '学生', '儿童', '家庭', '便携', '旗舰店', '直播', '特价', '正品', '批发', '包邮', '囤货', '实惠'
]

const STOP_WORDS = [
    '旗舰店', '直播', '专享', '新款', '特价', '包邮', '正品', '官方', '男女', '学生', '一个', '一件', '两件', '三件', '四件',
    '颜色', '尺寸', '拍下', '现货', '厂家', '直销', '活动', '链接', '淘宝', '天猫', '拼多多', '京东'
]

const COLOR_LIST = [
    '#24c96f', '#2aa8d9', '#5fc76f', '#6d3d91', '#13a188', '#98d931', '#244b8f', '#7431a5',
    '#178fbe', '#7cc242', '#2f8fcb', '#4c6ccf', '#8bc53f', '#3eaf7c', '#5b3e96', '#00a6a6'
]

const BASE_POSITIONS = [
    [50, 48, 0], [43, 42, 0], [57, 42, 0], [46, 56, 0], [55, 56, 0], [50, 36, 0],
    [39, 50, -8], [62, 50, 8], [48, 64, 90], [53, 66, 90], [42, 33, 0], [58, 32, 0],
    [36, 40, 0], [65, 39, 0], [35, 58, 0], [66, 58, 0], [50, 27, 0], [44, 72, 0],
    [57, 72, 0], [31, 49, -90], [70, 48, 90], [37, 28, 0], [64, 27, 0], [29, 36, -10],
    [72, 36, 10], [29, 63, 0], [72, 63, 0], [50, 78, 0], [40, 74, -8], [61, 75, 8]
]

export default {
    name: 'WordCloudView',
    data() {
        return {
            loading: false,
            cloudWords: [],
            productList: [],
        }
    },
    computed: {
        mode() {
            return this.$route.meta && this.$route.meta.wordType === 'address' ? 'address' : 'product'
        },
        cloudTitle() {
            return this.mode === 'address' ? '地址词云图' : '商品词云图'
        },
    },
    watch: {
        '$route.name'() {
            this.refreshCloud()
        },
    },
    mounted() {
        this.fetchData()
    },
    methods: {
        async fetchData() {
            this.loading = true
            try {
                const res = await this.$http.get('myApp/productList', {
                    params: {
                        page: 1,
                        pageSize: 10000,
                    },
                })
                const body = res.data || res
                this.productList = Array.isArray(body.data) ? body.data : []
                this.refreshCloud()
            } catch (e) {
                this.$Message.error('词云图数据接口请求失败')
                this.cloudWords = []
            } finally {
                this.loading = false
            }
        },
        refreshCloud() {
            if (this.mode === 'address') {
                this.cloudWords = this.buildAddressWords(this.productList)
            } else {
                this.cloudWords = this.buildProductWords(this.productList)
            }
        },
        buildProductWords(list) {
            const counter = new Map()
            list.forEach(item => {
                const title = String(item.title || item.productName || item.name || '')
                const type = String(item.type || '').trim()
                if (type) this.addWord(counter, type, 6)

                PRODUCT_KEYWORDS.forEach(word => {
                    const count = this.countText(title, word)
                    if (count > 0) this.addWord(counter, word, count * 4)
                })

                this.extractTextWords(title).forEach(word => {
                    this.addWord(counter, word, 1)
                })
            })
            return this.toCloudWords(counter, 90)
        },
        buildAddressWords(list) {
            const counter = new Map()
            list.forEach(item => {
                const area = this.normalizeArea(item.address || item.province || item.city)
                if (area) this.addWord(counter, area, Number(item.buy_len || item.sales || 1) || 1)
            })
            return this.toCloudWords(counter, 60)
        },
        extractTextWords(text) {
            const result = []
            const cleaned = String(text || '')
                .replace(/[0-9]+(g|kg|ml|cm|mm|斤|包|袋|盒|箱|瓶|支|片|抽|卷|件|条)?/gi, ' ')
                .replace(/[A-Za-z]+/g, ' ')
                .replace(/[【】\[\]（）()《》<>，。、“”‘’!！?？：:；;\/\\|_+=~·.-]/g, ' ')
            const parts = cleaned.split(/\s+/).filter(Boolean)
            parts.forEach(part => {
                const word = part.trim()
                if (word.length >= 2 && word.length <= 6 && STOP_WORDS.indexOf(word) === -1) {
                    result.push(word)
                }
                if (word.length > 6) {
                    for (let i = 0; i < word.length - 1; i += 2) {
                        const child = word.substr(i, 2)
                        if (STOP_WORDS.indexOf(child) === -1) result.push(child)
                    }
                }
            })
            return result
        },
        toCloudWords(counter, limit) {
            const arr = Array.from(counter.keys()).map(name => ({
                name,
                value: counter.get(name),
            })).filter(item => item.name && item.value > 0)
                .sort((a, b) => b.value - a.value)
                .slice(0, limit)

            const values = arr.map(item => item.value)
            const max = values.length ? Math.max.apply(null, values) : 1
            const min = values.length ? Math.min.apply(null, values) : 0
            const span = Math.max(max - min, 1)

            return arr.map((item, index) => {
                const position = this.getPosition(index)
                const ratio = (item.value - min) / span
                return {
                    ...item,
                    left: position[0],
                    top: position[1],
                    rotate: position[2],
                    size: Math.round(13 + ratio * 34 + (index < 5 ? 8 : 0)),
                    color: COLOR_LIST[index % COLOR_LIST.length],
                    zIndex: 200 - index,
                    opacity: index < 45 ? 1 : 0.82,
                }
            })
        },
        getPosition(index) {
            if (BASE_POSITIONS[index]) return BASE_POSITIONS[index]
            const angle = index * 137.5 * Math.PI / 180
            const radius = 24 + Math.floor(index / 8) * 2.3
            const left = this.clamp(50 + Math.cos(angle) * radius, 10, 90)
            const top = this.clamp(50 + Math.sin(angle) * radius * 0.72, 14, 88)
            const rotate = index % 9 === 0 ? 90 : (index % 5 === 0 ? -90 : 0)
            return [left, top, rotate]
        },
        getWordStyle(item) {
            return {
                left: item.left + '%',
                top: item.top + '%',
                fontSize: item.size + 'px',
                color: item.color,
                transform: `translate(-50%, -50%) rotate(${item.rotate}deg)`,
                zIndex: item.zIndex,
                opacity: item.opacity,
            }
        },
        addWord(counter, word, value) {
            const name = String(word || '').trim()
            if (!name || name.length < 2 || STOP_WORDS.indexOf(name) !== -1) return
            counter.set(name, (counter.get(name) || 0) + value)
        },
        countText(text, word) {
            if (!text || !word) return 0
            const reg = new RegExp(word, 'g')
            const match = String(text).match(reg)
            return match ? match.length : 0
        },
        normalizeArea(value) {
            const text = String(value || '').trim()
            if (!text) return ''
            return text
                .replace(/省|市|壮族自治区|回族自治区|维吾尔自治区|自治区|特别行政区/g, '')
                .replace(/\s+/g, '')
        },
        clamp(value, min, max) {
            return Math.max(min, Math.min(max, value))
        },
    },
}
</script>

<style scoped>
.word-cloud-page {
    min-height: calc(100vh - 90px);
    padding: 0 12px 18px;
    background: #f4f7fb;
}

.section-card {
    background: #fff;
    border: 1px solid #e6e9ef;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, .06);
}

.chart-card {
    min-height: 590px;
}

.section-title {
    height: 50px;
    line-height: 50px;
    padding: 0 20px;
    font-size: 16px;
    color: #333;
    border-bottom: 1px solid #e6e9ef;
}

.cloud-shell {
    margin: 28px 35px 0;
    height: 430px;
    border: 1px solid #dcdee2;
    border-radius: 5px;
    background: #fff;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, .08);
}

.cloud-header {
    height: 54px;
    line-height: 54px;
    padding-left: 22px;
    font-size: 16px;
    color: #333;
    border-bottom: 1px solid #e6e9ef;
}

.cloud-canvas {
    position: relative;
    height: calc(100% - 54px);
    background: #fff;
    overflow: hidden;
}

.cloud-canvas.product::before {
    content: '';
    position: absolute;
    left: 50%;
    top: 53%;
    width: 380px;
    height: 260px;
    transform: translate(-50%, -50%);
    border-radius: 48% 52% 50% 50%;
    background: radial-gradient(circle, rgba(45, 201, 111, .08), rgba(255, 255, 255, 0) 65%);
}

.cloud-canvas.address::before {
    content: '';
    position: absolute;
    left: 50%;
    top: 52%;
    width: 460px;
    height: 290px;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    background: radial-gradient(circle, rgba(64, 158, 255, .08), rgba(255, 255, 255, 0) 68%);
}

.cloud-word {
    position: absolute;
    display: inline-block;
    white-space: nowrap;
    font-weight: 700;
    line-height: 1;
    letter-spacing: 1px;
    user-select: none;
    transition: transform .2s ease, opacity .2s ease;
}

.cloud-word:hover {
    opacity: 1 !important;
    filter: drop-shadow(0 3px 6px rgba(0, 0, 0, .22));
}

.cloud-empty {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    font-size: 15px;
}
</style>
