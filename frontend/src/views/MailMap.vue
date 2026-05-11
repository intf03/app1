<template>
    <div class="mail-map-page">
        <div class="section-card condition-card">
            <div class="section-title">▦ 条件选择</div>
            <div class="condition-body">
                <div class="condition-item">
                    <span class="dash">-</span>
                    <div class="field-wrap">
                        <div class="field-label">产品类型</div>
                        <Select v-model="query.delivery" placeholder="请选择" style="width: 190px">
                            <Option v-for="item in deliveryOptions" :key="item.value" :value="item.value">{{ item.label }}</Option>
                        </Select>
                    </div>
                </div>
                <Button type="primary" class="submit-btn" :loading="loading" @click="handleSubmit">提交</Button>
            </div>
        </div>

        <div class="section-card chart-card">
            <div class="section-title">▣ 图表</div>
            <div class="map-shell">
                <div class="map-title">▣ 邮寄地图</div>
                <div ref="mailMap" class="map-main"></div>
            </div>
        </div>
    </div>
</template>

<script>
import getMap from '@/api/getMap.js'

const GEO_MAP = {
    北京: [116.4074, 39.9042], 天津: [117.1902, 39.1256], 上海: [121.4737, 31.2304], 重庆: [106.5044, 29.5582],
    河北: [114.4995, 38.1006], 山西: [112.5624, 37.8735], 内蒙古: [111.6708, 40.8183], 辽宁: [123.4315, 41.8057],
    吉林: [125.3245, 43.8868], 黑龙江: [126.6424, 45.7567], 江苏: [118.7674, 32.0415], 浙江: [120.1551, 30.2741],
    安徽: [117.2849, 31.8612], 福建: [119.3062, 26.0753], 江西: [115.8922, 28.6765], 山东: [117.0009, 36.6758],
    河南: [113.6654, 34.757], 湖北: [114.2986, 30.5844], 湖南: [112.9823, 28.1941], 广东: [113.2644, 23.1291],
    广西: [108.32, 22.824], 海南: [110.3492, 20.0174], 四川: [104.0657, 30.6595], 贵州: [106.7092, 26.5783],
    云南: [102.7123, 25.0406], 西藏: [91.1409, 29.6564], 陕西: [108.948, 34.2632], 甘肃: [103.8236, 36.058],
    青海: [101.7807, 36.6209], 宁夏: [106.2782, 38.4664], 新疆: [87.6168, 43.8256], 台湾: [121.52, 25.03],
    香港: [114.1734, 22.321], 澳门: [113.543, 22.1987],
}

const AREA_ALIAS = {
    黑龙江省: '黑龙江', 吉林省: '吉林', 辽宁省: '辽宁', 河北省: '河北', 河南省: '河南', 山东省: '山东', 山西省: '山西',
    陕西省: '陕西', 甘肃省: '甘肃', 青海省: '青海', 江苏省: '江苏', 浙江省: '浙江', 安徽省: '安徽', 江西省: '江西',
    福建省: '福建', 湖北省: '湖北', 湖南省: '湖南', 广东省: '广东', 四川省: '四川', 贵州省: '贵州', 云南省: '云南',
    海南省: '海南', 北京市: '北京', 天津市: '天津', 上海市: '上海', 重庆市: '重庆', 广西壮族自治区: '广西',
    内蒙古自治区: '内蒙古', 宁夏回族自治区: '宁夏', 新疆维吾尔自治区: '新疆', 西藏自治区: '西藏', 香港特别行政区: '香港', 澳门特别行政区: '澳门',
}

export default {
    name: 'MailMap',
    data() {
        return {
            loading: false,
            chart: null,
            query: {
                delivery: '',
            },
            deliveryOptions: [
                { label: '不限', value: '' },
                { label: '包邮', value: '1' },
                { label: '不包邮', value: '0' },
            ],
        }
    },
    mounted() {
        window.addEventListener('resize', this.resizeChart)
        this.handleSubmit()
    },
    beforeDestroy() {
        window.removeEventListener('resize', this.resizeChart)
        if (this.chart) {
            this.chart.dispose()
            this.chart = null
        }
    },
    methods: {
        async handleSubmit() {
            this.loading = true
            try {
                const res = await this.$http.get('myApp/productList', {
                    params: {
                        page: 1,
                        pageSize: 10000,
                    },
                })
                const body = res.data || res
                const list = Array.isArray(body.data) ? body.data : []
                const filtered = this.filterByDelivery(list)
                const mapData = this.buildMapData(filtered)
                await this.renderMap(mapData)
            } catch (e) {
                this.$Message.error('邮寄分布图接口请求失败')
                await this.renderMap([])
            } finally {
                this.loading = false
            }
        },
        filterByDelivery(list) {
            if (this.query.delivery === '') return list
            return list.filter(item => String(this.normalizeDelivery(item.isFreeDelivery)) === this.query.delivery)
        },
        normalizeDelivery(value) {
            if (value === 1 || value === '1' || value === true || value === 'true' || value === '包邮') return '1'
            if (value === 0 || value === '0' || value === false || value === 'false' || value === '不包邮') return '0'
            return String(value || '')
        },
        buildMapData(list) {
            const counter = new Map()
            list.forEach(item => {
                const area = this.normalizeArea(item.address || item.province || item.city)
                if (!area || !GEO_MAP[area]) return
                const value = Number(item.buy_len || item.sales || item.count || 1) || 1
                counter.set(area, (counter.get(area) || 0) + value)
            })
            return Array.from(counter.keys()).map(name => ({
                name,
                value: GEO_MAP[name].concat(counter.get(name)),
            }))
        },
        normalizeArea(value) {
            if (!value) return ''
            const text = String(value).trim()
            if (AREA_ALIAS[text]) return AREA_ALIAS[text]
            return text
                .replace(/省|市|壮族自治区|回族自治区|维吾尔自治区|自治区|特别行政区/g, '')
                .replace(/\s+/g, '')
        },
        async renderMap(data) {
            const mapJson = await getMap()
            this.$echarts.registerMap('china', mapJson.data)
            this.$nextTick(() => {
                if (!this.chart) this.chart = this.$echarts.init(this.$refs.mailMap)
                const values = data.map(item => item.value[2])
                const max = values.length ? Math.max.apply(null, values) : 100

                this.chart.setOption({
                    backgroundColor: '#fff',
                    tooltip: {
                        trigger: 'item',
                        formatter: params => {
                            if (params.value && params.value.length > 2) {
                                return `${params.name}<br/>邮寄数量：${params.value[2]}`
                            }
                            return params.name || ''
                        },
                    },
                    visualMap: {
                        type: 'piecewise',
                        left: 260,
                        bottom: 28,
                        itemWidth: 46,
                        itemHeight: 18,
                        textStyle: { color: '#333', fontSize: 13 },
                        pieces: [
                            { min: max * 0.8, label: '非常多', color: '#61e36a' },
                            { min: max * 0.55, max: max * 0.8, label: '较多', color: '#8ed9ee' },
                            { min: max * 0.35, max: max * 0.55, label: '正常', color: '#fff23d' },
                            { min: max * 0.15, max: max * 0.35, label: '较少', color: '#f39c12' },
                            { min: 0, max: max * 0.15, label: '非常少', color: '#ef2b00' },
                        ],
                        dimension: 2,
                    },
                    geo: {
                        map: 'china',
                        roam: true,
                        zoom: 1.18,
                        layoutCenter: ['52%', '54%'],
                        layoutSize: '82%',
                        label: {
                            show: true,
                            color: '#333',
                            fontSize: 12,
                        },
                        itemStyle: {
                            areaColor: '#eef1ed',
                            borderColor: '#d1d6d3',
                            borderWidth: 1,
                        },
                        emphasis: {
                            label: { show: true, color: '#333' },
                            itemStyle: { areaColor: '#dce8df' },
                        },
                    },
                    series: [
                        {
                            name: '邮寄数量',
                            type: 'scatter',
                            coordinateSystem: 'geo',
                            data,
                            symbolSize: value => Math.max(7, Math.min(24, Number(value[2]) / Math.max(max, 1) * 32)),
                            label: {
                                show: true,
                                formatter: '{b}',
                                position: 'right',
                                color: '#333',
                                fontSize: 12,
                            },
                            itemStyle: {
                                borderColor: '#fff',
                                borderWidth: 1,
                            },
                            emphasis: {
                                scale: true,
                                label: { show: true },
                            },
                        },
                    ],
                }, true)
                this.resizeChart()
            })
        },
        resizeChart() {
            if (this.chart) this.chart.resize()
        },
    },
}
</script>

<style scoped>
.mail-map-page {
    min-height: calc(100vh - 90px);
    padding: 0 0 18px;
    background: #f4f7fb;
}

.section-card {
    background: #fff;
    border: 1px solid #e6e9ef;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, .06);
    margin-bottom: 10px;
}

.condition-card {
    min-height: 200px;
}

.section-title {
    height: 50px;
    line-height: 50px;
    padding: 0 20px;
    font-size: 16px;
    color: #333;
    border-bottom: 1px solid #e6e9ef;
}

.condition-body {
    display: flex;
    align-items: center;
    gap: 64px;
    padding: 30px 0 0 48px;
}

.condition-item {
    display: flex;
    align-items: flex-start;
    gap: 28px;
}

.dash {
    font-size: 18px;
    color: #333;
    line-height: 30px;
}

.field-label {
    font-size: 15px;
    color: #333;
    margin-bottom: 10px;
}

.submit-btn {
    margin-top: 28px;
    width: 76px;
    height: 38px;
}

.chart-card {
    min-height: 690px;
}

.map-shell {
    margin: 28px 35px 0;
    height: 585px;
    border: 1px solid #dcdee2;
    border-radius: 5px;
    background: #fff;
    overflow: hidden;
}

.map-title {
    height: 54px;
    line-height: 54px;
    padding-left: 22px;
    font-size: 16px;
    color: #333;
    border-bottom: 1px solid #e6e9ef;
}

.map-main {
    width: 100%;
    height: calc(100% - 54px);
}
</style>
