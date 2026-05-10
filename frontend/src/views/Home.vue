<template>
  <div class="dashboard-page" ref="layoutRef">
    <div class="dashboard-stage" :style="screenStyle">
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
          <div
            ref="firstMain"
            class="chart-box left-top-chart"
            @mouseenter="startAction"
            @mouseleave="cancelAction"
          ></div>
        </dv-border-box-13>

        <dv-border-box-8 class="panel left-bottom">
          <div ref="secondMain" class="chart-box"></div>
        </dv-border-box-8>

        <div class="center-map">
          <div ref="thirdMain" class="map-box"></div>
        </div>

        <dv-border-box-12 class="panel right-top">
          <dv-decoration-3 class="panel-deco right-deco" />
          <div ref="rightTopMain" class="chart-box right-chart"></div>
        </dv-border-box-12>

        <dv-border-box-1 class="panel right-bottom">
          <div ref="rightBottomMain" class="chart-box right-chart"></div>
        </dv-border-box-1>
      </div>
    </div>
  </div>
</template>

<script>
import getMap from "@/api/getMap.js"

export default {
  data() {
    return {
      designWidth: 1680,
      designHeight: 900,
      screenScale: 1,
      screenLeft: 0,
      screenTop: 0,

      isHovered: true,
      timer: null,
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
        priceRangeList: ["0-100", "100-200", "200-500", "500-1000", "千元以上"],
        priceRangeValueList: [0, 0, 0, 0, 0],
        typeSalesList: []
      }
    }
  },

  computed: {
    screenStyle() {
      return {
        transform: `scale(${this.screenScale})`,
        left: `${this.screenLeft}px`,
        top: `${this.screenTop}px`
      }
    }
  },

  methods: {
    initScale() {
      const box = this.$refs.layoutRef
      const rect = box ? box.getBoundingClientRect() : null
      const ww = rect && rect.width ? rect.width : window.innerWidth
      let wh = rect && rect.height ? rect.height : window.innerHeight

      if (wh < 420) {
        wh = window.innerHeight - 90
      }

      const scale = Math.min(ww / this.designWidth, wh / this.designHeight)
      this.screenScale = scale
      this.screenLeft = Math.max((ww - this.designWidth * scale) / 2, 0)
      this.screenTop = Math.max((wh - this.designHeight * scale) / 2, 0)
    },

    initChart(refName, chartKey) {
      if (!this[chartKey]) {
        this[chartKey] = this.$echarts.init(this.$refs[refName])
      }
      return this[chartKey]
    },

    drawLeftTop() {
      const myChart = this.initChart("firstMain", "chart")
      const option = {
        backgroundColor: "transparent",
        title: {
          text: "各地区销售数据",
          left: "center",
          top: 20,
          textStyle: {
            color: "#e8f7ff",
            fontSize: 24,
            fontWeight: "bold"
          }
        },
        grid: {
          left: 60,
          right: 52,
          top: 92,
          bottom: 48
        },
        toolbox: {
          show: true,
          right: 22,
          top: 34,
          iconStyle: {
            borderColor: "#75bfff"
          },
          feature: {
            magicType: { show: true, type: ["line", "bar"] },
            restore: { show: true },
            saveAsImage: { show: true }
          }
        },
        legend: {
          data: ["销售数据"],
          top: 55,
          right: 46,
          textStyle: {
            color: "#c7d8ea"
          }
        },
        tooltip: {
          trigger: "axis"
        },
        xAxis: {
          type: "category",
          data: this.realData.cityList,
          axisLine: {
            lineStyle: {
              color: "rgba(210,235,255,.75)"
            }
          },
          axisLabel: {
            color: "#d9edff",
            fontSize: 15
          }
        },
        yAxis: {
          type: "value",
          axisLine: {
            lineStyle: {
              color: "rgba(210,235,255,.75)"
            }
          },
          splitLine: {
            lineStyle: {
              color: "rgba(210,235,255,.55)"
            }
          },
          axisLabel: {
            color: "#d9edff",
            fontSize: 15
          }
        },
        series: [
          {
            name: "销售数据",
            data: this.realData.volumnList,
            type: "bar",
            barWidth: 42,
            itemStyle: {
              color: "#4f6fe0"
            },
            label: {
              show: true,
              position: "inside",
              color: "#d8e1ff",
              fontSize: 14
            }
          }
        ]
      }
      myChart.setOption(option, true)
    },

    drawLeftBottom() {
      const myChart = this.initChart("secondMain", "secondChart")
      const option = {
        backgroundColor: "transparent",
        title: {
          text: "各类型产品占比",
          left: "center",
          top: 18,
          textStyle: {
            color: "#e8f7ff",
            fontSize: 24,
            fontWeight: "bold"
          }
        },
        tooltip: {
          trigger: "item",
          formatter: "{b}<br/>数量：{c}<br/>占比：{d}%"
        },
        legend: {
          orient: "vertical",
          left: 24,
          top: 74,
          itemWidth: 22,
          itemHeight: 14,
          textStyle: {
            color: "#d7ecff",
            fontSize: 15
          }
        },
        series: [
          {
            name: "数量",
            type: "pie",
            radius: "47%",
            center: ["60%", "56%"],
            data: this.realData.pieList,
            label: {
              show: true,
              color: "#e3f4ff",
              fontSize: 15
            },
            labelLine: {
              lineStyle: {
                color: "#65cfff"
              }
            },
            emphasis: {
              itemStyle: {
                shadowBlur: 15,
                shadowColor: "rgba(0, 0, 0, 0.5)"
              }
            }
          }
        ]
      }
      myChart.setOption(option, true)
    },

    async drawCenterMap() {
      const myChart = this.initChart("thirdMain", "mapChart")
      const res = await getMap()
      this.$echarts.registerMap("china", res.data)
      const data = this.realData.mapData
      const geoCoordMap = {
        北京市: [116.4074, 39.9042], 北京: [116.4074, 39.9042],
        天津市: [117.1902, 39.1256], 天津: [117.1902, 39.1256],
        上海市: [121.4737, 31.2304], 上海: [121.4737, 31.2304],
        重庆市: [106.5044, 29.5582], 重庆: [106.5044, 29.5582],
        河北省: [114.4995, 38.1006], 河北: [114.4995, 38.1006],
        山西省: [112.5624, 37.8735], 山西: [112.5624, 37.8735],
        内蒙古自治区: [111.6708, 40.8183], 内蒙古: [111.6708, 40.8183],
        辽宁省: [123.4315, 41.8057], 辽宁: [123.4315, 41.8057],
        吉林省: [125.3245, 43.8868], 吉林: [125.3245, 43.8868],
        黑龙江省: [126.6424, 45.7567], 黑龙江: [126.6424, 45.7567],
        江苏省: [118.7674, 32.0415], 江苏: [118.7674, 32.0415],
        浙江省: [120.1551, 30.2741], 浙江: [120.1551, 30.2741],
        安徽省: [117.2849, 31.8612], 安徽: [117.2849, 31.8612],
        福建省: [119.3062, 26.0753], 福建: [119.3062, 26.0753],
        江西省: [115.8922, 28.6765], 江西: [115.8922, 28.6765],
        山东省: [117.0009, 36.6758], 山东: [117.0009, 36.6758],
        河南省: [113.6654, 34.757], 河南: [113.6654, 34.757],
        湖北省: [114.2986, 30.5844], 湖北: [114.2986, 30.5844],
        湖南省: [112.9823, 28.1941], 湖南: [112.9823, 28.1941],
        广东省: [113.2644, 23.1291], 广东: [113.2644, 23.1291],
        广西壮族自治区: [108.32, 22.824], 广西: [108.32, 22.824],
        海南省: [110.3492, 20.0174], 海南: [110.3492, 20.0174],
        四川省: [104.0657, 30.6595], 四川: [104.0657, 30.6595],
        贵州省: [106.7092, 26.5783], 贵州: [106.7092, 26.5783],
        云南省: [102.7123, 25.0406], 云南: [102.7123, 25.0406],
        西藏自治区: [91.1409, 29.6564], 西藏: [91.1409, 29.6564],
        陕西省: [108.948, 34.2632], 陕西: [108.948, 34.2632],
        甘肃省: [103.8236, 36.058], 甘肃: [103.8236, 36.058],
        青海省: [101.7807, 36.6209], 青海: [101.7807, 36.6209],
        宁夏回族自治区: [106.2782, 38.4664], 宁夏: [106.2782, 38.4664],
        新疆维吾尔自治区: [87.6168, 43.8256], 新疆: [87.6168, 43.8256],
        台湾省: [121.52, 25.03], 台湾: [121.52, 25.03],
        香港特别行政区: [114.1734, 22.321], 香港: [114.1734, 22.321],
        澳门特别行政区: [113.543, 22.1987], 澳门: [113.543, 22.1987]
      }
      const convertData = function(list) {
        const result = []
        for (let i = 0; i < list.length; i++) {
          const rawName = String(list[i].name || "")
          const name = rawName.split(/\s+/)[0]
          const geoCoord = geoCoordMap[rawName] || geoCoordMap[name]
          if (geoCoord) {
            result.push({
              name: name,
              value: geoCoord.concat(list[i].value)
            })
          }
        }
        return result
      }
      const option = {
        backgroundColor: "transparent",
        title: {
          text: "全国省市产品数据",
          subtext: "数据来自淘宝",
          left: "center",
          top: 122,
          textStyle: {
            color: "#ffffff",
            fontSize: 25,
            fontWeight: "bold"
          },
          subtextStyle: {
            color: "#8fb4d8",
            fontSize: 15
          }
        },
        geo: {
          show: true,
          map: "china",
          roam: false,
          layoutCenter: ["50%", "55%"],
          layoutSize: "84%",
          label: {
            show: true,
            color: "#ffffff",
            fontSize: 11
          },
          itemStyle: {
            areaColor: "#8bd7e8",
            borderColor: "#ffffff",
            borderWidth: 1
          },
          emphasis: {
            label: {
              show: true,
              color: "#ffffff"
            },
            itemStyle: {
              areaColor: "#2b91b7"
            }
          }
        },
        series: [
          {
            name: "销量",
            type: "effectScatter",
            coordinateSystem: "geo",
            data: convertData(data),
            symbolSize: function(val) {
              return Math.max(8, Math.min(24, val[2] / 10))
            },
            showEffectOn: "render",
            rippleEffect: {
              brushType: "stroke"
            },
            label: {
              formatter: "{b}",
              position: "right",
              show: true,
              color: "#fff"
            },
            itemStyle: {
              color: "#ddb926"
            }
          }
        ]
      }
      myChart.setOption(option, true)
    },

    drawRightTop() {
      const myChart = this.initChart("rightTopMain", "rightTopChart")
      const option = {
        backgroundColor: "transparent",
        title: {
          text: "商品价格占比",
          left: "center",
          top: 24,
          textStyle: {
            color: "#e8f7ff",
            fontSize: 24,
            fontWeight: "bold"
          }
        },
        grid: {
          left: 65,
          right: 46,
          top: 100,
          bottom: 58
        },
        tooltip: {
          trigger: "axis"
        },
        legend: {
          data: ["占比情况"],
          top: 60,
          right: 38,
          textStyle: {
            color: "#d7ecff"
          }
        },
        xAxis: {
          type: "category",
          data: this.realData.priceRangeList,
          axisLabel: {
            color: "#d7ecff",
            fontSize: 15
          },
          axisLine: {
            lineStyle: {
              color: "rgba(210,235,255,.65)"
            }
          }
        },
        yAxis: {
          type: "value",
          axisLabel: {
            color: "#d7ecff",
            fontSize: 15
          },
          splitLine: {
            lineStyle: {
              color: "rgba(210,235,255,.55)"
            }
          }
        },
        series: [
          {
            name: "占比情况",
            type: "line",
            smooth: true,
            symbolSize: 8,
            data: this.realData.priceRangeValueList,
            lineStyle: {
              width: 3,
              color: "#7b8cff"
            },
            itemStyle: {
              color: "#7b8cff"
            }
          }
        ]
      }
      myChart.setOption(option, true)
    },

    drawRightBottom() {
      const myChart = this.initChart("rightBottomMain", "rightBottomChart")
      const dataList = this.realData.typeSalesList && this.realData.typeSalesList.length
        ? this.realData.typeSalesList
        : [{ name: "暂无数据", value: 0 }]
      const total = dataList.reduce(function(sum, item) {
        return sum + Number(item.value || 0)
      }, 0)
      const maxItem = dataList[0] || { name: "暂无数据", value: 0 }
      const percent = total > 0 ? Math.round((Number(maxItem.value || 0) / total) * 100) : 0
      const centerText = percent + "%\n" + maxItem.name

      const option = {
        backgroundColor: "transparent",
        title: {
          text: "各类型销售量占比",
          left: "center",
          top: 24,
          textStyle: {
            color: "#e8f7ff",
            fontSize: 24,
            fontWeight: "bold"
          }
        },
        tooltip: {
          trigger: "item",
          formatter: "{b}<br/>销量：{c}<br/>占比：{d}%"
        },
        series: [
          {
            name: "销售量",
            type: "pie",
            radius: ["42%", "66%"],
            center: ["50%", "58%"],
            data: dataList,
            label: {
              show: true,
              position: "center",
              formatter: function(params) {
                return params.name === maxItem.name ? centerText : ""
              },
              color: "#ffffff",
              fontSize: 26,
              lineHeight: 38
            },
            labelLine: {
              show: false
            }
          }
        ]
      }
      myChart.setOption(option, true)
    },

    async drawAllCharts() {
      this.drawLeftTop()
      this.drawLeftBottom()
      await this.drawCenterMap()
      this.drawRightTop()
      this.drawRightBottom()
    },

    changeData(list) {
      if (!Array.isArray(list) || list.length <= 1) return
      const first = list[0]
      for (let i = 0; i < list.length - 1; i++) {
        list[i] = list[i + 1]
      }
      list[list.length - 1] = first
    },

    updateBarChart() {
      if (this.isHovered === true && this.chart) {
        this.changeData(this.realData.cityList)
        this.changeData(this.realData.volumnList)
        this.chart.setOption({
          xAxis: {
            data: this.realData.cityList
          },
          series: [
            {
              data: this.realData.volumnList
            }
          ]
        })
      }
    },

    startDataUpdataInterval() {
      clearInterval(this.timer)
      this.timer = setInterval(this.updateBarChart, 2000)
    },

    startAction() {
      this.isHovered = false
    },

    cancelAction() {
      this.isHovered = true
    },

    handleResize() {
      this.initScale()
      this.$nextTick(() => {
        if (this.chart) this.chart.resize()
        if (this.secondChart) this.secondChart.resize()
        if (this.mapChart) this.mapChart.resize()
        if (this.rightTopChart) this.rightTopChart.resize()
        if (this.rightBottomChart) this.rightBottomChart.resize()
      })
    }
  },

  async mounted() {
    this.$nextTick(() => {
      this.initScale()
    })

    window.addEventListener("resize", this.handleResize)

    const res = await this.$http.get("myApp/screenData")
    const data = res.data || res

    this.$set(this.realData, "cityList", data.cityList || [])
    this.$set(this.realData, "volumnList", data.volumnList || [])
    this.$set(this.realData, "pieList", data.pieList || [])
    this.$set(this.realData, "mapData", data.mapData || [])
    this.$set(this.realData, "priceRangeList", data.priceRangeList || ["0-100", "100-200", "200-500", "500-1000", "千元以上"])
    this.$set(this.realData, "priceRangeValueList", data.priceRangeValueList || [0, 0, 0, 0, 0])
    this.$set(this.realData, "typeSalesList", data.typeSalesList || [])

    this.$nextTick(async () => {
      this.initScale()
      await this.drawAllCharts()
      this.startDataUpdataInterval()
    })
  },

  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize)
    clearInterval(this.timer)
    if (this.chart) this.chart.dispose()
    if (this.secondChart) this.secondChart.dispose()
    if (this.mapChart) this.mapChart.dispose()
    if (this.rightTopChart) this.rightTopChart.dispose()
    if (this.rightBottomChart) this.rightBottomChart.dispose()
  }
}
</script>

<style scoped>
.dashboard-page {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 760px;
  overflow: hidden;
  background: #020b1a;
}

.dashboard-stage {
  position: absolute;
  width: 1680px;
  height: 900px;
  transform-origin: left top;
  color: #dff6ff;
  background: url('../assets/imgs/bg.jpg') no-repeat center center;
  background-size: cover;
  overflow: hidden;
}

.dashboard-header {
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-deco {
  width: 430px;
  height: 62px;
}

.header-center {
  width: 480px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.title-text {
  color: #4e9bd4;
  font-size: 32px;
  font-weight: bold;
  letter-spacing: 2px;
  line-height: 42px;
}

.title-deco {
  width: 360px;
  height: 42px;
}

.dashboard-grid {
  height: 800px;
  padding: 18px 28px 36px 6px;
  box-sizing: border-box;
  display: grid;
  grid-template-columns: 500px 1fr 500px;
  grid-template-rows: 360px 360px;
  column-gap: 34px;
  row-gap: 24px;
}

.panel {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.left-top {
  grid-column: 1;
  grid-row: 1;
}

.left-bottom {
  grid-column: 1;
  grid-row: 2;
}

.center-map {
  grid-column: 2;
  grid-row: 1 / 3;
  position: relative;
  min-width: 0;
  min-height: 0;
}

.right-top {
  grid-column: 3;
  grid-row: 1;
}

.right-bottom {
  grid-column: 3;
  grid-row: 2;
}

.chart-box {
  position: absolute;
  inset: 18px;
}

.left-top-chart {
  inset: 38px 18px 16px 18px;
}

.right-chart {
  inset: 22px 22px 18px 22px;
}

.map-box {
  width: 100%;
  height: 100%;
}

.panel-deco {
  position: absolute;
  z-index: 2;
}

.left-deco {
  width: 220px;
  height: 24px;
  top: 12px;
  left: 28px;
}

.right-deco {
  width: 310px;
  height: 26px;
  top: 16px;
  left: 34px;
}
</style>
