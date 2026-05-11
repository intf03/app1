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
            <div class="section-title">▣ 机器学习销量预测结果</div>
            <div class="predict-shell">
                <div class="predict-title">▣ {{ algorithmName }}情况</div>
                <div class="predict-main">
                    <div class="result-panel">
                        <div class="main-result">销量： {{ formatDecimal(predictionValue) }}</div>
                        <div class="algorithm-name">{{ modelName }}</div>
                        <div class="result-desc">{{ modelDescription }}</div>
                    </div>

                    <div class="summary-grid">
                        <div class="summary-card">
                            <div class="summary-label">有效样本</div>
                            <div class="summary-value">{{ sampleCount }}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">训练样本</div>
                            <div class="summary-value">{{ trainCount }}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">测试样本</div>
                            <div class="summary-value">{{ testCount }}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">MAE</div>
                            <div class="summary-value">{{ formatDecimal(metrics.mae) }}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">RMSE</div>
                            <div class="summary-value">{{ formatDecimal(metrics.rmse) }}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">R²</div>
                            <div class="summary-value">{{ formatMetric(metrics.r2) }}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">历史均值</div>
                            <div class="summary-value">{{ formatDecimal(historyAverage) }}</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-label">价格输入</div>
                            <div class="summary-value">{{ formatDecimal(query.price) }}</div>
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
        desc: '使用 scikit-learn LinearRegression，根据商品价格、类型、地址和包邮状态训练回归模型。',
        chartTitle: '价格-销量预测趋势',
    },
    knn: {
        title: 'KNN近邻回归预测',
        desc: '使用 scikit-learn KNeighborsRegressor，基于相似商品样本估算销量。',
        chartTitle: '近邻商品销量参考',
    },
    weighted: {
        title: '相似度加权回归预测',
        desc: '使用相似度样本权重训练加权线性回归模型，距离越近的样本权重越高。',
        chartTitle: '相似样本权重与销量',
    },
    tree: {
        title: '决策树回归预测',
        desc: '使用 scikit-learn DecisionTreeRegressor 学习商品特征与销量之间的非线性关系。',
        chartTitle: '分组样本销量均值',
    },
    forest: {
        title: '随机森林回归预测',
        desc: '使用 scikit-learn RandomForestRegressor 进行集成回归预测。',
        chartTitle: '分组样本销量均值',
    },
}

export default {
    name: 'SalesPredict',
    data() {
        return {
            loading: false,
            chart: null,
            typeList: [],
            addressList: [],
            predictionValue: 0,
            historyAverage: 0,
            sampleCount: 0,
            trainCount: 0,
            testCount: 0,
            algorithmName: '机器学习预测',
            modelName: 'scikit-learn',
            modelDescription: '基于商品样本训练回归模型，对输入商品销量进行辅助预测。',
            metrics: {
                mae: 0,
                rmse: 0,
                r2: 0,
            },
            similarSamples: [],
            chartData: [],
            query: {
                type: '',
                price: '200',
                address: '',
                delivery: '',
            },
            deliveryOptions: [
                { label: '不限', value: '' },
                { label: '包邮', value: '1' },
                { label: '不包邮', value: '0' },
            ],
            sampleColumns: [
                { title: '商品类型', key: 'type', width: 90, align: 'center' },
                {
                    title: '价格',
                    key: 'price',
                    width: 80,
                    align: 'center',
                    render: (h, params) => h('span', this.formatDecimal(params.row.price)),
                },
                { title: '地址', key: 'address', width: 85, align: 'center' },
                { title: '包邮', key: 'deliveryText', width: 70, align: 'center' },
                {
                    title: '销量',
                    key: 'sales',
                    width: 85,
                    align: 'center',
                    render: (h, params) => h('span', this.formatDecimal(params.row.sales)),
                },
                {
                    title: '相似度权重',
                    key: 'weight',
                    width: 105,
                    align: 'center',
                    render: (h, params) => h('span', this.formatMetric(params.row.weight)),
                },
                { title: '商品名', key: 'title', minWidth: 180, tooltip: true },
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
            this.handlePredict()
        },
    },
    mounted() {
        window.addEventListener('resize', this.resizeChart)
        this.handlePredict()
    },
    beforeDestroy() {
        window.removeEventListener('resize', this.resizeChart)
        if (this.chart) {
            this.chart.dispose()
            this.chart = null
        }
    },
    methods: {
        async handlePredict() {
            this.loading = true
            try {
                const res = await this.$http.get('myApp/mlPredict', {
                    params: {
                        algorithm: this.algorithmType,
                        type: this.query.type,
                        price: this.query.price,
                        address: this.query.address,
                        delivery: this.query.delivery,
                    },
                })
                const body = res.data || res
                if (body.code !== 0) {
                    this.$Message.warning(body.msg || '机器学习预测失败')
                    return
                }
                const data = body.data || {}
                this.typeList = data.typeList || []
                this.addressList = data.addressList || []
                if (!this.query.type && data.input && data.input.type) this.query.type = data.input.type
                if (!this.query.address && data.input && data.input.address) this.query.address = data.input.address
                if (data.input && data.input.price) this.query.price = String(data.input.price)
                if (data.input && data.input.delivery !== undefined) this.query.delivery = data.input.delivery

                this.predictionValue = data.predictionValue || 0
                this.historyAverage = data.historyAverage || 0
                this.sampleCount = data.sampleCount || 0
                this.trainCount = data.trainCount || 0
                this.testCount = data.testCount || 0
                this.algorithmName = data.algorithmName || this.currentAlgorithm.title
                this.modelName = data.modelName || 'scikit-learn'
                this.modelDescription = data.modelDescription || this.currentAlgorithm.desc
                this.metrics = data.metrics || { mae: 0, rmse: 0, r2: 0 }
                this.similarSamples = data.similarSamples || []
                this.chartData = data.chartData || []
                this.drawChart()
            } catch (e) {
                this.$Message.error('机器学习预测接口请求失败')
            } finally {
                this.loading = false
            }
        },
        drawChart() {
            this.$nextTick(() => {
                if (!this.$refs.predictChart) return
                if (!this.chart) this.chart = this.$echarts.init(this.$refs.predictChart)

                const names = this.chartData.map(item => item.name)
                const values = this.chartData.map(item => Number(this.formatDecimal(item.value)))
                const isLine = this.algorithmType === 'linear' || this.algorithmType === 'weighted'

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
                        name: '销量',
                        axisLabel: { color: '#666' },
                        splitLine: { lineStyle: { color: '#e6e9ef' } },
                    },
                    series: [
                        {
                            name: '销量',
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
        safeNumber(value) {
            const num = Number(value)
            if (!isFinite(num) || isNaN(num)) return 0
            return Math.max(0, num)
        },
        formatDecimal(value) {
            const num = this.safeNumber(value)
            return Number(num.toFixed(1))
        },
        formatMetric(value) {
            const num = Number(value)
            if (!isFinite(num) || isNaN(num)) return 0
            return Number(num.toFixed(4))
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
    min-height: 138px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
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
    max-width: 920px;
    margin-top: 8px;
    color: #999;
    font-size: 14px;
    line-height: 22px;
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
    grid-template-columns: 1fr 620px;
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
