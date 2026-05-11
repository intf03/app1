<template>
    <div class="sales-predict-page">
        <div class="section-card condition-card">
            <div class="section-title">▦ 条件选择</div>
            <div class="condition-body">
                <div class="condition-item">
                    <span class="dash">-</span>
                    <div class="field-wrap">
                        <div class="field-label">产品类型</div>
                        <Select v-model="query.type" clearable placeholder="请选择" style="width: 190px">
                            <Option v-for="item in typeList" :key="item" :value="item">{{ item }}</Option>
                        </Select>
                    </div>
                </div>

                <div class="condition-item">
                    <span class="dash">-</span>
                    <div class="field-wrap">
                        <div class="field-label">产品价格</div>
                        <Input v-model="query.price" placeholder="请输入价格" style="width: 190px" />
                    </div>
                </div>

                <div class="condition-item">
                    <span class="dash">-</span>
                    <div class="field-wrap">
                        <div class="field-label">产品地址</div>
                        <Select v-model="query.address" clearable placeholder="请选择" style="width: 190px">
                            <Option v-for="item in addressList" :key="item" :value="item">{{ item }}</Option>
                        </Select>
                    </div>
                </div>

                <div class="condition-item">
                    <span class="dash">-</span>
                    <div class="field-wrap">
                        <div class="field-label">包邮情况</div>
                        <Select v-model="query.delivery" placeholder="请选择" style="width: 190px">
                            <Option v-for="item in deliveryOptions" :key="item.value" :value="item.value">{{ item.label }}</Option>
                        </Select>
                    </div>
                </div>

                <Button type="primary" class="submit-btn" :loading="loading" @click="handlePredict">提交</Button>
            </div>
        </div>

        <div class="section-card data-card">
            <div class="section-title">▣ 数据</div>
            <div class="predict-shell">
                <div class="predict-title">▣ {{ currentAlgorithm.title }}情况</div>
                <div class="predict-main">
                    <div class="result-panel">
                        <div class="main-result">销量： {{ formatDecimal(predictionValue) }}</div>
                        <div class="algorithm-name">{{ currentAlgorithm.title }}</div>
                        <div class="result-desc">{{ currentAlgorithm.desc }}</div>
                    </div>

                    <div class="summary-grid">
                        <div class="summary-card">
                            <div class="summary-label">训练样本</div>
                            <div class="summary-value">{{ trainData.length }}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">参考样本</div>
                            <div class="summary-value">{{ availableRecords.length }}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">历史均值</div>
                            <div class="summary-value">{{ formatDecimal(historyAverage) }}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">价格输入</div>
                            <div class="summary-value">{{ formatDecimal(toNumber(query.price)) }}</div>
                        </div>
                    </div>

                    <div class="chart-row">
                        <div ref="predictChart" class="predict-chart"></div>
                        <div class="sample-box">
                            <div class="sample-title">相似商品参考</div>
                            <Table
                                size="small"
                                :columns="sampleColumns"
                                :data="similarSamples"
                                height="230"
                            ></Table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
const ALGORITHM_MAP = {
    linear: {
        title: '线性回归预测',
        desc: '根据历史商品价格与销量之间的线性关系，估算当前输入商品的销量。',
        chartTitle: '价格-销量线性趋势',
    },
    knn: {
        title: 'KNN近邻预测',
        desc: '寻找与当前商品在类型、价格、地址、包邮情况上最相似的商品，按近邻销量加权估算。',
        chartTitle: '近邻商品销量参考',
    },
    weighted: {
        title: '相似度加权预测',
        desc: '对所有历史商品按相似度计算权重，权重越高的商品对预测销量影响越大。',
        chartTitle: '相似度权重分布',
    },
    tree: {
        title: '分组决策树预测',
        desc: '按照产品类型、地址和包邮情况逐层分组，取最匹配分组的历史销量均值。',
        chartTitle: '分组层级预测',
    },
}

export default {
    name: 'SalesPredict',
    data() {
        return {
            loading: false,
            chart: null,
            rawProducts: [],
            trainData: [],
            typeList: [],
            addressList: [],
            predictionValue: 0,
            historyAverage: 0,
            availableRecords: [],
            similarSamples: [],
            chartData: [],
            query: {
                type: '服装',
                price: '200',
                address: '广东',
                delivery: '0',
            },
            deliveryOptions: [
                { label: '不限', value: '' },
                { label: '包邮', value: '1' },
                { label: '不包邮', value: '0' },
            ],
            sampleColumns: [
                {
                    title: '商品类型',
                    key: 'type',
                    width: 90,
                    align: 'center',
                },
                {
                    title: '价格',
                    key: 'price',
                    width: 80,
                    align: 'center',
                    render: (h, params) => h('span', this.formatDecimal(params.row.price)),
                },
                {
                    title: '地址',
                    key: 'address',
                    width: 85,
                    align: 'center',
                },
                {
                    title: '包邮',
                    key: 'deliveryText',
                    width: 70,
                    align: 'center',
                },
                {
                    title: '销量',
                    key: 'sales',
                    width: 85,
                    align: 'center',
                    render: (h, params) => h('span', this.formatDecimal(params.row.sales)),
                },
                {
                    title: '商品名',
                    key: 'title',
                    minWidth: 180,
                    tooltip: true,
                },
            ],
        }
    },
    computed: {
        algorithmType() {
            return (this.$route.meta && this.$route.meta.algorithm) || 'linear'
        },
        currentAlgorithm() {
            return ALGORITHM_MAP[this.algorithmType] || ALGORITHM_MAP.linear
        },
    },
    watch: {
        '$route.name'() {
            this.runPrediction()
        },
    },
    mounted() {
        window.addEventListener('resize', this.resizeChart)
        this.fetchData()
    },
    beforeDestroy() {
        window.removeEventListener('resize', this.resizeChart)
        if (this.chart) {
            this.chart.dispose()
            this.chart = null
        }
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
                this.rawProducts = Array.isArray(body.data) ? body.data : []
                this.trainData = this.rawProducts.map(this.normalizeProduct).filter(item => item.sales > 0)
                this.typeList = body.typeList || this.getUniqueList(this.trainData, 'type')
                this.addressList = body.addressList || this.getUniqueList(this.trainData, 'address')
                this.setDefaultQuery()
                this.runPrediction()
            } catch (e) {
                this.$Message.error('销量预测数据接口请求失败')
                this.trainData = []
                this.predictionValue = 0
                this.availableRecords = []
                this.similarSamples = []
            } finally {
                this.loading = false
            }
        },
        handlePredict() {
            if (!this.trainData.length) {
                this.$Message.warning('暂无可用于预测的商品数据')
                return
            }
            this.runPrediction()
        },
        runPrediction() {
            if (!this.trainData.length) return
            const input = this.getInput()
            const records = this.getAvailableRecords(input)
            this.availableRecords = records
            this.historyAverage = this.average(records, 'sales')

            if (this.algorithmType === 'knn') {
                this.predictionValue = this.knnPredict(records, input)
                this.chartData = this.getSimilarSamples(records, input).map((item, index) => ({ name: '近邻' + (index + 1), value: item.sales }))
            } else if (this.algorithmType === 'weighted') {
                this.predictionValue = this.weightedSimilarityPredict(records, input)
                this.chartData = this.getWeightedChartData(records, input)
            } else if (this.algorithmType === 'tree') {
                const treeResult = this.groupDecisionPredict(input)
                this.predictionValue = treeResult.value
                this.chartData = treeResult.levels
            } else {
                const linearResult = this.linearRegressionPredict(records, input)
                this.predictionValue = linearResult.value
                this.chartData = linearResult.points
            }

            this.similarSamples = this.getSimilarSamples(records, input)
            this.drawChart()
        },
        getInput() {
            return {
                type: this.query.type || '',
                price: this.toNumber(this.query.price),
                address: this.query.address || '',
                delivery: this.query.delivery,
            }
        },
        getAvailableRecords(input) {
            const strict = this.trainData.filter(item => {
                const typeOk = !input.type || item.type === input.type
                const addressOk = !input.address || item.address === input.address
                const deliveryOk = input.delivery === '' || item.delivery === input.delivery
                return typeOk && addressOk && deliveryOk
            })
            if (strict.length >= 3) return strict

            const medium = this.trainData.filter(item => {
                const typeOk = !input.type || item.type === input.type
                const deliveryOk = input.delivery === '' || item.delivery === input.delivery
                return typeOk && deliveryOk
            })
            if (medium.length >= 3) return medium

            return this.trainData.slice()
        },
        linearRegressionPredict(records, input) {
            if (!records.length) return { value: 0, points: [] }
            const usable = records.filter(item => item.price > 0 && item.sales > 0)
            if (usable.length < 2) {
                return {
                    value: this.average(records, 'sales'),
                    points: records.slice(0, 10).map(item => ({ name: this.formatDecimal(item.price), value: item.sales })),
                }
            }

            const xAvg = this.average(usable, 'price')
            const yAvg = this.average(usable, 'sales')
            let numerator = 0
            let denominator = 0
            usable.forEach(item => {
                numerator += (item.price - xAvg) * (item.sales - yAvg)
                denominator += Math.pow(item.price - xAvg, 2)
            })
            if (!denominator) {
                return { value: yAvg, points: usable.slice(0, 10).map(item => ({ name: this.formatDecimal(item.price), value: item.sales })) }
            }
            const slope = numerator / denominator
            const intercept = yAvg - slope * xAvg
            const predicted = this.clampPrediction(intercept + slope * input.price)
            const points = usable.sort((a, b) => a.price - b.price).slice(0, 12).map(item => ({
                name: this.formatDecimal(item.price),
                value: item.sales,
            }))
            points.push({ name: '预测价' + this.formatDecimal(input.price), value: predicted })
            return { value: predicted, points }
        },
        knnPredict(records, input) {
            const nearest = this.getSimilarSamples(records, input)
            if (!nearest.length) return 0
            let totalWeight = 0
            let totalValue = 0
            nearest.forEach(item => {
                const weight = 1 / (item.distance + 0.08)
                totalWeight += weight
                totalValue += item.sales * weight
            })
            return this.clampPrediction(totalValue / Math.max(totalWeight, 1))
        },
        weightedSimilarityPredict(records, input) {
            if (!records.length) return 0
            let totalWeight = 0
            let totalValue = 0
            records.forEach(item => {
                const distance = this.calcDistance(item, input)
                const weight = Math.exp(-distance * 1.5)
                totalWeight += weight
                totalValue += item.sales * weight
            })
            return this.clampPrediction(totalValue / Math.max(totalWeight, 1))
        },
        groupDecisionPredict(input) {
            const groups = [
                { name: '类型+地址+包邮', filter: item => item.type === input.type && item.address === input.address && item.delivery === input.delivery },
                { name: '类型+地址', filter: item => item.type === input.type && item.address === input.address },
                { name: '类型+包邮', filter: item => item.type === input.type && item.delivery === input.delivery },
                { name: '产品类型', filter: item => item.type === input.type },
                { name: '产品地址', filter: item => item.address === input.address },
                { name: '全部样本', filter: () => true },
            ]
            const levels = []
            let result = 0
            for (let i = 0; i < groups.length; i++) {
                const matched = this.trainData.filter(groups[i].filter)
                const avg = this.average(matched, 'sales')
                levels.push({ name: groups[i].name, value: avg, count: matched.length })
                if (!result && matched.length >= 3) result = avg
            }
            return {
                value: this.clampPrediction(result || this.average(this.trainData, 'sales')),
                levels,
            }
        },
        getSimilarSamples(records, input) {
            return records.map(item => ({
                ...item,
                distance: this.calcDistance(item, input),
            })).sort((a, b) => a.distance - b.distance).slice(0, 8)
        },
        getWeightedChartData(records, input) {
            return this.getSimilarSamples(records, input).map((item, index) => ({
                name: '样本' + (index + 1),
                value: Number((Math.exp(-item.distance * 1.5) * 100).toFixed(2)),
                sales: item.sales,
            }))
        },
        calcDistance(item, input) {
            const priceList = this.trainData.map(row => row.price || 0).concat([input.price, 1])
            const maxPrice = Math.max.apply(null, priceList)
            const priceDistance = Math.abs((item.price || 0) - input.price) / Math.max(maxPrice, 1)
            const typeDistance = input.type && item.type !== input.type ? 0.9 : 0
            const addressDistance = input.address && item.address !== input.address ? 0.65 : 0
            const deliveryDistance = input.delivery !== '' && item.delivery !== input.delivery ? 0.45 : 0
            return priceDistance + typeDistance + addressDistance + deliveryDistance
        },
        drawChart() {
            this.$nextTick(() => {
                if (!this.$refs.predictChart) return
                if (!this.chart) this.chart = this.$echarts.init(this.$refs.predictChart)

                const names = this.chartData.map(item => item.name)
                const values = this.chartData.map(item => Number(this.formatDecimal(item.value)))
                const isLine = this.algorithmType === 'linear'

                this.chart.setOption({
                    backgroundColor: '#fff',
                    title: {
                        text: this.currentAlgorithm.chartTitle,
                        left: 16,
                        top: 8,
                        textStyle: { fontSize: 15, color: '#333', fontWeight: 500 },
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: { type: isLine ? 'line' : 'shadow' },
                    },
                    grid: {
                        left: 70,
                        right: 28,
                        top: 58,
                        bottom: 48,
                    },
                    xAxis: {
                        type: 'category',
                        data: names,
                        axisLabel: { color: '#666' },
                    },
                    yAxis: {
                        type: 'value',
                        name: this.algorithmType === 'weighted' ? '权重' : '销量',
                        axisLabel: { color: '#666' },
                        splitLine: { lineStyle: { color: '#e6e9ef' } },
                    },
                    series: [
                        {
                            name: this.algorithmType === 'weighted' ? '相似权重' : '销量',
                            type: isLine ? 'line' : 'bar',
                            smooth: isLine,
                            barWidth: 36,
                            data: values,
                            label: {
                                show: true,
                                position: 'top',
                                formatter: params => this.formatDecimal(params.value),
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
        normalizeProduct(row) {
            const delivery = this.normalizeDelivery(row.isFreeDelivery)
            return {
                title: row.title || row.productName || row.name || '',
                type: String(row.type || '').trim(),
                price: this.toNumber(row.price || row.product_price || row.sale_price),
                address: String(row.address || row.province || row.city || '').trim(),
                delivery,
                deliveryText: delivery === '1' ? '包邮' : (delivery === '0' ? '不包邮' : '不限'),
                sales: this.toNumber(row.buy_len || row.sales || row.sale_num || row.num || row.count),
            }
        },
        normalizeDelivery(value) {
            if (value === 1 || value === '1' || value === true || value === 'true' || value === '包邮') return '1'
            if (value === 0 || value === '0' || value === false || value === 'false' || value === '不包邮') return '0'
            return ''
        },
        setDefaultQuery() {
            if (this.typeList.indexOf('服装') === -1 && this.typeList.length) this.query.type = this.typeList[0]
            if (this.addressList.indexOf('广东') === -1 && this.addressList.length) this.query.address = this.addressList[0]
            if (!this.query.price) this.query.price = '200'
        },
        getUniqueList(list, key) {
            return Array.from(new Set((list || []).map(item => item && item[key]).filter(Boolean)))
        },
        average(list, key) {
            if (!list || !list.length) return 0
            const sum = list.reduce((total, item) => total + this.toNumber(item[key]), 0)
            return sum / list.length
        },
        toNumber(value) {
            if (value === null || value === undefined || value === '') return 0
            const text = String(value).replace(/,/g, '').replace(/￥|元/g, '').trim()
            if (text.indexOf('万') !== -1) return Number(text.replace('万', '')) * 10000 || 0
            return Number(text) || 0
        },
        safeNumber(value) {
            if (!isFinite(value) || isNaN(value)) return 0
            return Math.max(0, value)
        },
        clampPrediction(value) {
            const safe = this.safeNumber(value)
            const maxSales = Math.max.apply(null, this.trainData.map(item => item.sales || 0).concat([safe, 1]))
            return Math.min(safe, maxSales * 1.25)
        },
        formatDecimal(value) {
            const num = this.safeNumber(Number(value))
            return Number(num.toFixed(1))
        },
    },
}
</script>

<style scoped>
.sales-predict-page {
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
    min-height: 190px;
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
    gap: 46px;
    padding: 30px 0 0 48px;
    flex-wrap: wrap;
}

.condition-item {
    display: flex;
    align-items: flex-start;
    gap: 24px;
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
    min-height: 560px;
}

.predict-shell {
    margin: 26px 34px 0;
    border: 1px solid #dcdee2;
    border-radius: 5px;
    background: #fff;
    overflow: hidden;
}

.predict-title {
    height: 52px;
    line-height: 52px;
    padding-left: 22px;
    font-size: 16px;
    color: #333;
    border-bottom: 1px solid #e6e9ef;
}

.predict-main {
    min-height: 460px;
    padding: 28px 34px 26px;
}

.result-panel {
    height: 130px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.main-result {
    font-size: 52px;
    line-height: 64px;
    color: #666;
    letter-spacing: 2px;
}

.algorithm-name {
    margin-top: 2px;
    color: #2d8cf0;
    font-size: 16px;
}

.result-desc {
    margin-top: 8px;
    color: #999;
    font-size: 14px;
}

.summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 6px 0 22px;
}

.summary-card {
    border: 1px solid #e6e9ef;
    border-radius: 5px;
    background: #fbfcff;
    padding: 12px 16px;
}

.summary-label {
    color: #999;
    font-size: 13px;
}

.summary-value {
    margin-top: 8px;
    color: #2d8cf0;
    font-size: 24px;
    font-weight: 600;
}

.chart-row {
    display: grid;
    grid-template-columns: 1fr 540px;
    gap: 20px;
}

.predict-chart {
    height: 265px;
    border: 1px solid #e6e9ef;
    border-radius: 5px;
}

.sample-box {
    height: 265px;
    border: 1px solid #e6e9ef;
    border-radius: 5px;
    overflow: hidden;
}

.sample-title {
    height: 34px;
    line-height: 34px;
    padding-left: 14px;
    color: #333;
    border-bottom: 1px solid #e6e9ef;
    background: #fbfcff;
}
</style>
