<template>
    <div class="line-chart-page">
        <div class="section-card condition-card">
            <div class="section-title">▦ 条件选择</div>
            <div class="condition-body">
                <div class="condition-item">
                    <span class="dash">-</span>
                    <div class="field-wrap">
                        <div class="field-label">产品类型</div>
                        <Select
                            v-model="query.type"
                            clearable
                            filterable
                            placeholder="请选择产品类型"
                            style="width: 190px"
                        >
                            <Option v-for="item in typeList" :key="item" :value="item">{{ item }}</Option>
                        </Select>
                    </div>
                </div>
                <Button type="primary" class="submit-btn" :loading="loading" @click="handleSubmit">提交</Button>
            </div>
        </div>

        <div class="section-card data-card">
            <div class="section-title">▣ 数据</div>
            <div class="chart-shell">
                <div v-show="!empty" ref="lineChart" class="chart-main"></div>
                <div v-show="empty" class="empty-box">暂无对应产品类型的数据</div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'LineChart',
    data() {
        return {
            loading: false,
            empty: false,
            chart: null,
            allProducts: [],
            typeList: [],
            query: {
                type: '',
            },
        }
    },
    async mounted() {
        window.addEventListener('resize', this.resizeChart)
        await this.initPage()
    },
    beforeDestroy() {
        window.removeEventListener('resize', this.resizeChart)
        if (this.chart) {
            this.chart.dispose()
            this.chart = null
        }
    },
    methods: {
        async initPage() {
            this.loading = true
            try {
                const firstData = await this.getProductData({ page: 1, pageSize: 10000 })
                this.allProducts = firstData.list
                this.typeList = firstData.typeList.length ? firstData.typeList : this.getUniqueTypes(firstData.list)

                if (!this.query.type && this.typeList.length) {
                    this.query.type = this.typeList.includes('日用品') ? '日用品' : this.typeList[0]
                }

                this.drawByProducts(this.filterProductsByType(firstData.list))
            } catch (e) {
                await this.drawByScreenData()
            } finally {
                this.loading = false
            }
        },
        async handleSubmit() {
            this.loading = true
            try {
                const result = await this.getProductData({
                    page: 1,
                    pageSize: 10000,
                    type: this.query.type,
                })
                const products = result.list.length ? result.list : this.filterProductsByType(this.allProducts)

                if (result.typeList.length) this.typeList = result.typeList
                this.drawByProducts(products)
            } catch (e) {
                await this.drawByScreenData()
            } finally {
                this.loading = false
            }
        },
        async getProductData(params) {
            const res = await this.$http.get('myApp/productList', { params })
            const body = res.data || res
            const list = Array.isArray(body.data) ? body.data : []
            const typeList = Array.isArray(body.typeList) ? body.typeList : []
            return { list, typeList }
        },
        getUniqueTypes(list) {
            const set = new Set()
            list.forEach(item => {
                if (item && item.type) set.add(String(item.type).trim())
            })
            return Array.from(set).filter(Boolean)
        },
        filterProductsByType(list) {
            if (!this.query.type) return list
            return list.filter(item => String(item.type || '').trim() === this.query.type)
        },
        drawByProducts(list) {
            const summaryMap = new Map()

            list.forEach(item => {
                const area = this.formatArea(item.address || item.province || item.city || '未知')
                const price = this.toNumber(item.price || item.product_price || item.sale_price)
                const quantity = this.toNumber(item.buy_len || item.sales || item.sale_num || item.num || item.count)
                const amount = this.toNumber(item.sales_amount || item.saleAmount || item.totalPrice) || price * quantity

                if (!summaryMap.has(area)) {
                    summaryMap.set(area, { area, amount: 0, quantity: 0 })
                }
                const current = summaryMap.get(area)
                current.amount += amount
                current.quantity += quantity
            })

            const chartData = Array.from(summaryMap.values())
                .filter(item => item.area && item.area !== '未知')
                .sort((a, b) => b.amount - a.amount)
                .slice(0, 20)

            this.renderChart({
                areas: chartData.map(item => item.area),
                amountList: chartData.map(item => Math.round(item.amount)),
                quantityList: chartData.map(item => Math.round(item.quantity)),
            })
        },
        async drawByScreenData() {
            try {
                const res = await this.$http.get('myApp/screenData', {
                    params: { type: this.query.type },
                })
                const body = res.data || res
                const cityList = body.cityList || []
                const volumnList = body.volumnList || []
                this.renderChart({
                    areas: cityList.map(item => this.formatArea(item)),
                    amountList: volumnList.map(item => this.toNumber(item)),
                    quantityList: volumnList.map(item => this.toNumber(item)),
                })
            } catch (e) {
                this.renderChart({ areas: [], amountList: [], quantityList: [] })
                this.$Message.error('数据折线图接口请求失败')
            }
        },
        renderChart({ areas, amountList, quantityList }) {
            this.empty = !areas.length
            this.$nextTick(() => {
                if (this.empty) return
                if (!this.chart) this.chart = this.$echarts.init(this.$refs.lineChart)

                this.chart.setOption({
                    backgroundColor: '#fff',
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: { type: 'line' },
                        formatter: params => {
                            const title = params && params.length ? params[0].axisValue : ''
                            const rows = params.map(item => {
                                const unit = item.seriesName === '销售额' ? '元' : '件'
                                return `${item.marker}${item.seriesName}：${this.formatNumber(item.value)} ${unit}`
                            })
                            return [title].concat(rows).join('<br/>')
                        },
                    },
                    legend: {
                        top: 34,
                        right: 210,
                        data: ['销售额', '销售量'],
                    },
                    toolbox: {
                        right: 24,
                        top: 22,
                        feature: {
                            restore: { show: true },
                            saveAsImage: { show: true },
                        },
                    },
                    grid: {
                        left: 95,
                        right: 125,
                        top: 82,
                        bottom: 58,
                    },
                    xAxis: {
                        type: 'category',
                        boundaryGap: false,
                        data: areas,
                        axisTick: { alignWithLabel: true },
                        axisLabel: {
                            color: '#333',
                            interval: 0,
                        },
                    },
                    yAxis: [
                        {
                            type: 'value',
                            name: '销售额',
                            position: 'left',
                            axisLabel: {
                                formatter: value => this.formatNumber(value),
                            },
                            splitLine: {
                                lineStyle: { color: '#e5e8ef' },
                            },
                        },
                        {
                            type: 'value',
                            name: '销售量',
                            position: 'right',
                            axisLabel: {
                                formatter: value => this.formatNumber(value),
                            },
                            splitLine: { show: false },
                        },
                    ],
                    series: [
                        {
                            name: '销售额',
                            type: 'line',
                            smooth: false,
                            symbol: 'circle',
                            symbolSize: 7,
                            yAxisIndex: 0,
                            data: amountList,
                        },
                        {
                            name: '销售量',
                            type: 'line',
                            smooth: false,
                            symbol: 'circle',
                            symbolSize: 7,
                            yAxisIndex: 1,
                            data: quantityList,
                        },
                    ],
                }, true)
                this.resizeChart()
            })
        },
        resizeChart() {
            if (this.chart) this.chart.resize()
        },
        formatArea(value) {
            return String(value || '')
                .replace(/省|市|壮族自治区|回族自治区|维吾尔自治区|自治区|特别行政区/g, '')
                .trim()
        },
        toNumber(value) {
            if (value === null || value === undefined || value === '') return 0
            const text = String(value).replace(/,/g, '').replace(/￥|元/g, '').trim()
            if (text.includes('万')) return Number(text.replace('万', '')) * 10000 || 0
            return Number(text) || 0
        },
        formatNumber(value) {
            return Number(value || 0).toLocaleString()
        },
    },
}
</script>

<style scoped>
.line-chart-page {
    min-height: calc(100vh - 90px);
    padding: 0 12px 18px;
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
    min-height: 205px;
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
    padding: 30px 0 0 38px;
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

.data-card {
    min-height: 470px;
}

.chart-shell {
    margin: 20px;
    height: 365px;
    border: 1px solid #dcdee2;
    border-radius: 5px;
    background: #fff;
    position: relative;
}

.chart-main {
    width: 100%;
    height: 100%;
}

.empty-box {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    font-size: 15px;
}
</style>
