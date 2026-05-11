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
                <div class="predict-title">▣ 预测情况</div>
                <div class="predict-main">
                    <div class="result-panel">
                        <div class="main-result">销量： {{ formatDecimal(finalPrediction) }}</div>
                        <div class="result-desc">
                            综合线性回归、KNN相似商品、相似度加权、分组决策树四种算法的预测结果
                        </div>
                    </div>

                    <div class="algorithm-grid">
                        <div v-for="item in algorithmResults" :key="item.name" class="algorithm-card">
                            <div class="algo-name">{{ item.name }}</div>
                            <div class="algo-value">{{ formatDecimal(item.value) }}</div>
                            <div class="algo-desc">{{ item.desc }}</div>
                        </div>
                    </div>

                    <div class="chart-row">
                        <div ref="algorithmChart" class="algorithm-chart"></div>
                        <div class="sample-box">
                            <div class="sample-title">相似商品参考</div>
                            <Table
                                size="small"
                                :columns="sampleColumns"
                                :data="similarSamples"
                                height="210"
                            ></Table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
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
            finalPrediction: 0,
            algorithmResults: [],
            similarSamples: [],
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
                this.algorithmResults = []
                this.similarSamples = []
                this.finalPrediction = 0
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
            const input = {
                type: this.query.type || '',
                price: this.toNumber(this.query.price),
                address: this.query.address || '',
                delivery: this.query.delivery,
            }

            const baseRecords = this.getAvailableRecords()
            const linear = this.linearRegressionPredict(baseRecords, input)
            const knn = this.knnPredict(baseRecords, input)
            const weighted = this.weightedSimilarityPredict(baseRecords, input)
            const tree = this.groupDecisionPredict(baseRecords, input)

            this.algorithmResults = [
                { name: '线性回归', value: linear, desc: '根据价格与销量关系估算' },
                { name: 'KNN近邻回归', value: knn, desc: '参考最相似商品的销量' },
                { name: '相似度加权', value: weighted, desc: '按类型、价格、地区、包邮综合加权' },
                { name: '分组决策树', value: tree, desc: '按商品属性分组取历史均值' },
            ]

            this.finalPrediction = this.safeNumber(linear * 0.25 + knn * 0.3 + weighted * 0.25 + tree * 0.2)
            this.similarSamples = this.getSimilarSamples(baseRecords, input)
            this.drawAlgorithmChart()
        },
        getAvailableRecords() {
            const delivery = this.query.delivery
            const strict = this.trainData.filter(item => {
                const typeOk = !this.query.type || item.type === this.query.type
                const addressOk = !this.query.address || item.address === this.query.address
                const deliveryOk = delivery === '' || item.delivery === delivery
                return typeOk && addressOk && deliveryOk
            })
            if (strict.length >= 3) return strict

            const medium = this.trainData.filter(item => {
                const typeOk = !this.query.type || item.type === this.query.type
                const deliveryOk = delivery === '' || item.delivery === delivery
                return typeOk && deliveryOk
            })
            if (medium.length >= 3) return medium

            return this.trainData.slice()
        },
        linearRegressionPredict(records, input) {
            if (!records.length) return 0
            const usable = records.filter(item => item.price > 0 && item.sales > 0)
            if (usable.length < 2) return this.average(records, 'sales')

            const xAvg = this.average(usable, 'price')
            const yAvg = this.average(usable, 'sales')
            let numerator = 0
            let denominator = 0
            usable.forEach(item => {
                numerator += (item.price - xAvg) * (item.sales - yAvg)
                denominator += Math.pow(item.price - xAvg, 2)
            })
            if (!denominator) return yAvg
            const slope = numerator / denominator
            const intercept = yAvg - slope * xAvg
            return this.clampPrediction(intercept + slope * input.price)
        },
        knnPredict(records, input) {
            if (!records.length) return 0
            const sorted = records.map(item => ({
                ...item,
                distance: this.calcDistance(item, input),
            })).sort((a, b) => a.distance - b.distance)
            const k = Math.min(8, sorted.length)
            const nearest = sorted.slice(0, k)
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
        groupDecisionPredict(records, input) {
            const levels = [
                item => item.type === input.type && item.address === input.address && item.delivery === input.delivery,
                item => item.type === input.type && item.address === input.address,
                item => item.type === input.type && item.delivery === input.delivery,
                item => item.type === input.type,
                item => item.address === input.address,
                () => true,
            ]
            for (let i = 0; i < levels.length; i++) {
                const group = this.trainData.filter(levels[i])
                if (group.length >= 3) return this.clampPrediction(this.average(group, 'sales'))
            }
            return this.clampPrediction(this.average(records, 'sales'))
        },
        getSimilarSamples(records, input) {
            return records.map(item => ({
                ...item,
                distance: this.calcDistance(item, input),
            })).sort((a, b) => a.distance - b.distance).slice(0, 8)
        },
        calcDistance(item, input) {
            const maxPrice = Math.max.apply(null, this.trainData.map(row => row.price || 0).concat([input.price, 1]))
            const priceDistance = Math.abs((item.price || 0) - input.price) / Math.max(maxPrice, 1)
            const typeDistance = input.type && item.type !== input.type ? 0.9 : 0
            const addressDistance = input.address && item.address !== input.address ? 0.65 : 0
            const deliveryDistance = input.delivery !== '' && item.delivery !== input.delivery ? 0.45 : 0
            return priceDistance + typeDistance + addressDistance + deliveryDistance
        },
        drawAlgorithmChart() {
            this.$nextTick(() => {
                if (!this.$refs.algorithmChart) return
                if (!this.chart) this.chart = this.$echarts.init(this.$refs.algorithmChart)
                const names = this.algorithmResults.map(item => item.name)
                const values = this.algorithmResults.map(item => Number(this.formatDecimal(item.value)))
                this.chart.setOption({
                    backgroundColor: '#fff',
                    title: {
                        text: '多算法预测对比',
                        left: 16,
                        top: 8,
                        textStyle: { fontSize: 15, color: '#333', fontWeight: 500 },
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: { type: 'shadow' },
                        formatter: params => {
                            const item = params[0]
                            return `${item.name}<br/>预测销量：${this.formatDecimal(item.value)}`
                        },
                    },
                    grid: {
                        left: 70,
                        right: 28,
                        top: 56,
                        bottom: 42,
                    },
                    xAxis: {
                        type: 'category',
                        data: names,
                        axisLabel: { color: '#666' },
                    },
                    yAxis: {
                        type: 'value',
                        name: '销量',
                        axisLabel: { color: '#666' },
                        splitLine: { lineStyle: { color: '#e6e9ef' } },
                    },
                    series: [
                        {
                            name: '预测销量',
                            type: 'bar',
                            barWidth: 38,
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
    min-height: 520px;
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
    min-height: 430px;
    padding: 30px 34px 26px;
}

.result-panel {
    height: 132px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.main-result {
    font-size: 52px;
    line-height: 68px;
    color: #666;
    letter-spacing: 2px;
}

.result-desc {
    margin-top: 8px;
    color: #999;
    font-size: 14px;
}

.algorithm-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 10px 0 24px;
}

.algorithm-card {
    border: 1px solid #e6e9ef;
    border-radius: 5px;
    padding: 14px 16px;
    background: #fbfcff;
}

.algo-name {
    color: #333;
    font-size: 15px;
    margin-bottom: 8px;
}

.algo-value {
    color: #2d8cf0;
    font-size: 26px;
    font-weight: 600;
    line-height: 32px;
}

.algo-desc {
    color: #999;
    font-size: 12px;
    margin-top: 8px;
}

.chart-row {
    display: grid;
    grid-template-columns: 1fr 520px;
    gap: 20px;
}

.algorithm-chart {
    height: 245px;
    border: 1px solid #e6e9ef;
    border-radius: 5px;
}

.sample-box {
    height: 245px;
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
