<template>
  <div class="dashboard-page">
    <div class="dashboard-stage">
      <div class="dashboard-header">
        <dv-decoration-8 class="header-deco" />
        <div class="header-center">
          <div class="title-text">大数据可视化平台</div>
          <dv-decoration-5 class="title-deco" />
        </div>
        <dv-decoration-8 class="header-deco" :reverse="true" />
      </div>
      <div class="dashboard-grid">
        <dv-border-box-13 class="panel left-top">
          <dv-decoration-1 class="panel-deco left-deco" />
          <div ref="firstMain" class="chart-box left-top-chart" @mouseenter="startAction" @mouseleave="cancelAction"></div>
        </dv-border-box-13>
        <dv-border-box-8 class="panel left-bottom"><div ref="secondMain" class="chart-box"></div></dv-border-box-8>
        <div class="center-map"><div ref="thirdMain" class="map-box"></div></div>
        <dv-border-box-12 class="panel right-top">
          <dv-decoration-3 class="panel-deco right-deco" />
          <div ref="rightTopMain" class="chart-box right-chart"></div>
        </dv-border-box-12>
        <dv-border-box-1 class="panel right-bottom"><div ref="rightBottomMain" class="chart-box right-chart"></div></dv-border-box-1>
      </div>
    </div>
  </div>
</template>

<script>
import getMap from "@/api/getMap.js"

const PRICE_RANGE = ["0-100", "100-200", "200-500", "500-1000", "千元以上"]
const DONUT_COLORS = ["#4f6fe0", "#b8e62d", "#8df0a9", "#ffe45a", "#ff966f", "#4bc7d9", "#e85d93"]
const GEO_MAP = {
  北京: [116.4074, 39.9042], 天津: [117.1902, 39.1256], 上海: [121.4737, 31.2304], 重庆: [106.5044, 29.5582],
  河北: [114.4995, 38.1006], 山西: [112.5624, 37.8735], 内蒙古: [111.6708, 40.8183], 辽宁: [123.4315, 41.8057],
  吉林: [125.3245, 43.8868], 黑龙江: [126.6424, 45.7567], 江苏: [118.7674, 32.0415], 浙江: [120.1551, 30.2741],
  安徽: [117.2849, 31.8612], 福建: [119.3062, 26.0753], 江西: [115.8922, 28.6765], 山东: [117.0009, 36.6758],
  河南: [113.6654, 34.757], 湖北: [114.2986, 30.5844], 湖南: [112.9823, 28.1941], 广东: [113.2644, 23.1291],
  广西: [108.32, 22.824], 海南: [110.3492, 20.0174], 四川: [104.0657, 30.6595], 贵州: [106.7092, 26.5783],
  云南: [102.7123, 25.0406], 西藏: [91.1409, 29.6564], 陕西: [108.948, 34.2632], 甘肃: [103.8236, 36.058],
  青海: [101.7807, 36.6209], 宁夏: [106.2782, 38.4664], 新疆: [87.6168, 43.8256], 台湾: [121.52, 25.03],
  香港: [114.1734, 22.321], 澳门: [113.543, 22.1987]
}

export default {
  data() {
    return {
      isHovered: true,
      timer: null,
      typeTimer: null,
      currentTypeIndex: 0,
      chart: null,
      secondChart: null,
      mapChart: null,
      rightTopChart: null,
      rightBottomChart: null,
      realData: {
        cityList: [],
        volumnList: [],
        pieList: [],
        mapData: [],
        priceRangeList: PRICE_RANGE,
        priceRangeValueList: [0, 0, 0, 0, 0],
        typeSalesList: []
      }
    }
  },
  methods: {
    initChart(refName, chartKey) {
      if (!this[chartKey]) this[chartKey] = this.$echarts.init(this.$refs[refName])
      return this[chartKey]
    },
    drawLeftTop() {
      this.initChart("firstMain", "chart").setOption({
        backgroundColor: "transparent",
        title: { text: "各地区销售数据", left: 24, top: 16, textStyle: { color: "#e8f7ff", fontSize: 24, fontWeight: "bold" } },
        grid: { left: 60, right: 38, top: 92, bottom: 48 },
        toolbox: { show: true, right: 118, top: 18, itemSize: 16, iconStyle: { borderColor: "#75bfff" }, feature: { magicType: { show: true, type: ["line", "bar"] }, restore: { show: true }, saveAsImage: { show: true } } },
        legend: { data: ["销售数据"], top: 22, right: 20, itemWidth: 18, itemHeight: 10, textStyle: { color: "#c7d8ea", fontSize: 14 } },
        tooltip: { trigger: "axis" },
        xAxis: { type: "category", data: this.realData.cityList, axisLine: { lineStyle: { color: "rgba(210,235,255,.75)" } }, axisLabel: { color: "#d9edff", fontSize: 15 } },
        yAxis: { type: "value", axisLine: { lineStyle: { color: "rgba(210,235,255,.75)" } }, splitLine: { lineStyle: { color: "rgba(210,235,255,.55)" } }, axisLabel: { color: "#d9edff", fontSize: 15 } },
        series: [{ name: "销售数据", data: this.realData.volumnList, type: "bar", barWidth: 42, itemStyle: { color: "#4f6fe0" }, label: { show: true, position: "inside", color: "#d8e1ff", fontSize: 14 } }]
      }, true)
    },
    drawLeftBottom() {
      this.initChart("secondMain", "secondChart").setOption({
        backgroundColor: "transparent",
        title: { text: "各类型产品占比", left: "center", top: 18, textStyle: { color: "#e8f7ff", fontSize: 24, fontWeight: "bold" } },
        tooltip: { trigger: "item", formatter: "{b}<br/>数量：{c}<br/>占比：{d}%" },
        legend: { orient: "vertical", left: 24, top: 74, itemWidth: 22, itemHeight: 14, textStyle: { color: "#d7ecff", fontSize: 15 } },
        series: [{ name: "数量", type: "pie", radius: "47%", center: ["60%", "56%"], data: this.realData.pieList, label: { show: true, color: "#e3f4ff", fontSize: 15 }, labelLine: { lineStyle: { color: "#65cfff" } }, emphasis: { itemStyle: { shadowBlur: 15, shadowColor: "rgba(0,0,0,.5)" } } }]
      }, true)
    },
    normalizeAreaName(name) {
      return String(name || "").split(/\s+/)[0].replace(/省|市|壮族自治区|回族自治区|维吾尔自治区|自治区|特别行政区/g, "")
    },
    async drawCenterMap() {
      const myChart = this.initChart("thirdMain", "mapChart")
      const res = await getMap()
      this.$echarts.registerMap("china", res.data)
      const mapData = (this.realData.mapData || []).map(item => {
        const name = this.normalizeAreaName(item.name)
        return GEO_MAP[name] ? { name, value: GEO_MAP[name].concat(item.value) } : null
      }).filter(Boolean)
      myChart.setOption({
        backgroundColor: "transparent",
        title: { text: "全国省市产品数据", subtext: "数据来自淘宝", left: "center", top: 122, textStyle: { color: "#fff", fontSize: 25, fontWeight: "bold" }, subtextStyle: { color: "#8fb4d8", fontSize: 15 } },
        tooltip: { trigger: "item", formatter: p => p.value && p.value.length > 2 ? `${p.name}<br/>数量：${p.value[2]}` : (p.name || "") },
        geo: { show: true, map: "china", roam: true, zoom: 1, scaleLimit: { min: 0.75, max: 6 }, layoutCenter: ["50%", "55%"], layoutSize: "84%", label: { show: true, color: "#fff", fontSize: 11 }, itemStyle: { areaColor: "#8bd7e8", borderColor: "#fff", borderWidth: 1 }, emphasis: { label: { show: true, color: "#fff" }, itemStyle: { areaColor: "#2b91b7" } } },
        series: [{ name: "销量", type: "effectScatter", coordinateSystem: "geo", data: mapData, symbolSize: val => Math.max(8, Math.min(24, val[2] / 10)), showEffectOn: "render", rippleEffect: { brushType: "stroke" }, label: { formatter: "{b}", position: "right", show: true, color: "#fff" }, itemStyle: { color: "#ddb926" } }]
      }, true)
    },
    drawRightTop() {
      this.initChart("rightTopMain", "rightTopChart").setOption({
        backgroundColor: "transparent",
        title: { text: "商品价格占比", left: "center", top: 24, textStyle: { color: "#e8f7ff", fontSize: 24, fontWeight: "bold" } },
        grid: { left: 65, right: 46, top: 100, bottom: 58 },
        tooltip: { trigger: "axis" },
        legend: { data: ["占比情况"], top: 60, right: 38, textStyle: { color: "#d7ecff" } },
        xAxis: { type: "category", data: this.realData.priceRangeList, axisLabel: { color: "#d7ecff", fontSize: 15 }, axisLine: { lineStyle: { color: "rgba(210,235,255,.65)" } } },
        yAxis: { type: "value", axisLabel: { color: "#d7ecff", fontSize: 15 }, splitLine: { lineStyle: { color: "rgba(210,235,255,.55)" } } },
        series: [{ name: "占比情况", type: "line", smooth: true, symbolSize: 8, data: this.realData.priceRangeValueList, lineStyle: { width: 3, color: "#7b8cff" }, itemStyle: { color: "#7b8cff" } }]
      }, true)
    },
    drawRightBottom() {
      const myChart = this.initChart("rightBottomMain", "rightBottomChart")
      const source = this.realData.typeSalesList && this.realData.typeSalesList.length ? this.realData.typeSalesList : [{ name: "暂无数据", value: 0 }]
      const activeIndex = this.currentTypeIndex % source.length
      const dataList = source.map((item, index) => ({ name: item.name, value: Number(item.value || 0), selected: index === activeIndex, itemStyle: index === activeIndex ? { borderWidth: 3, borderColor: "#fff", shadowBlur: 22, shadowColor: "rgba(255,230,80,.72)" } : {} }))
      const total = dataList.reduce((sum, item) => sum + item.value, 0)
      const activeItem = dataList[activeIndex] || dataList[0]
      const percent = total > 0 ? Math.round(activeItem.value / total * 100) : 0
      const centerText = `${percent}%\n${activeItem.name}`
      myChart.setOption({
        backgroundColor: "transparent",
        color: DONUT_COLORS,
        title: { text: "各类型销售量占比", left: "center", top: 24, textStyle: { color: "#e8f7ff", fontSize: 24, fontWeight: "bold" } },
        tooltip: { trigger: "item", formatter: "{b}<br/>销量：{c}<br/>占比：{d}%" },
        series: [{ name: "销售量", type: "pie", radius: ["42%", "66%"], center: ["50%", "58%"], selectedMode: "single", selectedOffset: 18, data: dataList, label: { show: true, position: "center", formatter: p => p.name === activeItem.name ? centerText : "", color: "#fff", fontSize: 26, fontWeight: "bold", lineHeight: 38 }, labelLine: { show: false }, emphasis: { scale: true, scaleSize: 10, itemStyle: { shadowBlur: 28, shadowColor: "rgba(255,230,80,.8)" } } }]
      }, true)
      myChart.dispatchAction({ type: "downplay", seriesIndex: 0 })
      myChart.dispatchAction({ type: "highlight", seriesIndex: 0, dataIndex: activeIndex })
    },
    async drawAllCharts() {
      this.drawLeftTop(); this.drawLeftBottom(); await this.drawCenterMap(); this.drawRightTop(); this.drawRightBottom()
    },
    changeData(list) {
      if (!Array.isArray(list) || list.length <= 1) return
      const first = list[0]
      for (let i = 0; i < list.length - 1; i++) list[i] = list[i + 1]
      list[list.length - 1] = first
    },
    updateBarChart() {
      if (this.isHovered && this.chart) {
        this.changeData(this.realData.cityList); this.changeData(this.realData.volumnList)
        this.chart.setOption({ xAxis: { data: this.realData.cityList }, series: [{ data: this.realData.volumnList }] })
      }
    },
    startDataUpdataInterval() {
      clearInterval(this.timer)
      this.timer = setInterval(this.updateBarChart, 2000)
    },
    startTypeCarousel() {
      clearInterval(this.typeTimer)
      const list = this.realData.typeSalesList || []
      if (list.length <= 1) return
      this.typeTimer = setInterval(() => {
        this.currentTypeIndex = (this.currentTypeIndex + 1) % list.length
        this.drawRightBottom()
      }, 2400)
    },
    startAction() { this.isHovered = false },
    cancelAction() { this.isHovered = true },
    handleResize() {
      this.$nextTick(() => {
        if (this.chart) this.chart.resize(); if (this.secondChart) this.secondChart.resize(); if (this.mapChart) this.mapChart.resize(); if (this.rightTopChart) this.rightTopChart.resize(); if (this.rightBottomChart) this.rightBottomChart.resize()
      })
    }
  },
  async mounted() {
    window.addEventListener("resize", this.handleResize)
    const res = await this.$http.get("myApp/screenData")
    const data = res.data || res
    this.$set(this.realData, "cityList", data.cityList || [])
    this.$set(this.realData, "volumnList", data.volumnList || [])
    this.$set(this.realData, "pieList", data.pieList || [])
    this.$set(this.realData, "mapData", data.mapData || [])
    this.$set(this.realData, "priceRangeList", data.priceRangeList || PRICE_RANGE)
    this.$set(this.realData, "priceRangeValueList", data.priceRangeValueList || [0, 0, 0, 0, 0])
    this.$set(this.realData, "typeSalesList", data.typeSalesList || [])
    this.currentTypeIndex = 0
    this.$nextTick(async () => { await this.drawAllCharts(); this.startDataUpdataInterval(); this.startTypeCarousel() })
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize)
    clearInterval(this.timer)
    clearInterval(this.typeTimer)
    if (this.chart) this.chart.dispose(); if (this.secondChart) this.secondChart.dispose(); if (this.mapChart) this.mapChart.dispose(); if (this.rightTopChart) this.rightTopChart.dispose(); if (this.rightBottomChart) this.rightBottomChart.dispose()
  }
}
</script>

<style scoped>
.dashboard-page {
  width: 100%;
  min-height: calc(100vh - 90px);
  overflow: auto;
  background: #020b1a url('../assets/imgs/bg.jpg') no-repeat center top;
  background-size: cover;
}
.dashboard-stage {
  position: relative;
  width: 1680px;
  height: 900px;
  margin: 0 auto;
  color: #dff6ff;
  background: transparent;
  overflow: hidden;
}
.dashboard-header { height: 100px; display: flex; align-items: center; justify-content: center; }
.header-deco { width: 430px; height: 62px; }
.header-center { width: 480px; display: flex; flex-direction: column; align-items: center; }
.title-text { color: #4e9bd4; font-size: 32px; font-weight: bold; letter-spacing: 2px; line-height: 42px; }
.title-deco { width: 360px; height: 42px; }
.dashboard-grid { height: 800px; padding: 18px 28px 36px 6px; box-sizing: border-box; display: grid; grid-template-columns: 500px 1fr 500px; grid-template-rows: 360px 360px; column-gap: 34px; row-gap: 24px; }
.panel { position: relative; width: 100%; height: 100%; overflow: hidden; }
.left-top { grid-column: 1; grid-row: 1; }
.left-bottom { grid-column: 1; grid-row: 2; }
.center-map { grid-column: 2; grid-row: 1 / 3; position: relative; min-width: 0; min-height: 0; }
.right-top { grid-column: 3; grid-row: 1; }
.right-bottom { grid-column: 3; grid-row: 2; }
.chart-box { position: absolute; inset: 18px; }
.left-top-chart { inset: 38px 18px 16px 18px; }
.right-chart { inset: 22px 22px 18px 22px; }
.map-box { width: 100%; height: 100%; }
.panel-deco { position: absolute; z-index: 2; }
.left-deco { width: 220px; height: 24px; top: 12px; left: 28px; }
.right-deco { width: 310px; height: 26px; top: 16px; left: 34px; }
::v-deep .ivu-layout-content,
::v-deep .main-content {
  background: transparent !important;
}
</style>
