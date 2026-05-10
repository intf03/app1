<template>
<div class="layout">
    <div class="header">
      <dv-decoration-8 style="width:300px;height:50px;" />
        <div>
            <span class="title-text">商品数据可视化平台</span>
            <dv-decoration-5 style="width:300px;height:40px;" />
        </div>
        <dv-decoration-8 :reverse="true" style="width:300px;height:50px;" />
    </div>
    <div class="content">
        <div class="left">
            <dv-border-box-13>
                <dv-decoration-1 style="width:200px;height:20px;margin-top: 15px;" />
                <div
                ref="firstMain"
                style="width:100%;height:100%;"
                @mouseenter="startAction"
                @mouseleave="cancelAction"></div>
            </dv-border-box-13>
            <dv-border-box-8>
                <div ref="secondMain" style="width:100%;height:100%;"></div>
            </dv-border-box-8>
        </div>
        <div class="center">
            <div ref="thirdMain" style="width:450px;height:450px;"></div>
        </div>
        <div class="right">
            <dv-border-box-12>
                <dv-decoration-3 style="width:250px;height:20px; margin-top: 10px;" />
                <div ref="rightTopMain" style="width:100%;height:100%;"></div>
            </dv-border-box-12>
            <dv-border-box-1>
                <div ref="rightBottomMain" style="width:100%;height:100%;"></div>
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
      },
    };
  },
  methods: {
    initChart(refName, chartKey) {
      if (!this[chartKey]) {
        this[chartKey] = this.$echarts.init(this.$refs[refName]);
      }
      return this[chartKey];
    },

    drawLeftTop() {
      var myChart = this.initChart('firstMain', 'chart');
      var option = {
        xAxis: {
          type: 'category',
          data: this.realData.cityList,
          axisLabel: {
            textStyle: {
              color: "#c0c0c0",
            },
          },
        },
        dataZoom: [
          {
            type: "slider",
            start: 0,
            end: 85,
            show: false
          },
        ],
        title: {
          text: "各地区销售数据",
          left: "center",
          textStyle: {
            color: "#c0c0c0",
          },
        },
        toolbox: {
          show: true,
          feature: {
            magicType: { show: true, type: ["line", "bar"] },
            restore: { show: true },
            saveAsImage: { show: true },
          },
        },
        legend: {
          orient: "vertical",
          data: ["销售数据"],
          textStyle: {
            color: "grey",
          },
          top: "8%",
          left: "70%",
        },
        tooltip: {
          trigger: "item",
          formatter: "",
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            textStyle: {
              color: "#c0c0c0",
            },
          },
        },
        series: [
          {
            name: "销售数据",
            data: this.realData.volumnList,
            type: 'bar',
            label: {
              show: true,
              textStyle: {
                color: "#c0c0c0",
              },
            },
          },
        ],
      };
      myChart.setOption(option);
    },

    drawLeftBottom() {
      var myChart = this.initChart('secondMain', 'secondChart');
      var option = {
        title: {
          text: "各类产品占比",
          subtext: '',
          left: 'center',
          textStyle: {
            color: "#c0c0c0",
          },
        },
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          textStyle: {
            color: "#c0c0c0",
          },
        },
        series: [
          {
            name: "数量",
            type: 'pie',
            radius: '50%',
            data: this.realData.pieList,
            center: ["60%", "50%"],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)"
              },
            },
            label: {
              show: true,
              textStyle: {
                color: "#c0c0c0",
              },
            },
          },
        ],
      };
      myChart.setOption(option);
    },

    async drawCenterMap() {
      var myChart = this.initChart('thirdMain', 'mapChart');
      const res = await getMap();
      this.$echarts.registerMap("china", res.data);
      var data = this.realData.mapData;
      var geoCoordMap = {
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
        河南省: [113.6654, 34.7570], 河南: [113.6654, 34.7570],
        湖北省: [114.2986, 30.5844], 湖北: [114.2986, 30.5844],
        湖南省: [112.9823, 28.1941], 湖南: [112.9823, 28.1941],
        广东省: [113.2644, 23.1291], 广东: [113.2644, 23.1291],
        广西壮族自治区: [108.3200, 22.8240], 广西: [108.3200, 22.8240],
        海南省: [110.3492, 20.0174], 海南: [110.3492, 20.0174],
        四川省: [104.0657, 30.6595], 四川: [104.0657, 30.6595],
        贵州省: [106.7092, 26.5783], 贵州: [106.7092, 26.5783],
        云南省: [102.7123, 25.0406], 云南: [102.7123, 25.0406],
        西藏自治区: [91.1409, 29.6564], 西藏: [91.1409, 29.6564],
        陕西省: [108.9480, 34.2632], 陕西: [108.9480, 34.2632],
        甘肃省: [103.8236, 36.0580], 甘肃: [103.8236, 36.0580],
        青海省: [101.7807, 36.6209], 青海: [101.7807, 36.6209],
        宁夏回族自治区: [106.2782, 38.4664], 宁夏: [106.2782, 38.4664],
        新疆维吾尔自治区: [87.6168, 43.8256], 新疆: [87.6168, 43.8256],
        台湾省: [121.5200, 25.0300], 台湾: [121.5200, 25.0300],
        香港特别行政区: [114.1734, 22.3210], 香港: [114.1734, 22.3210],
        澳门特别行政区: [113.5430, 22.1987], 澳门: [113.5430, 22.1987],
      };
      var convertData = function(data) {
        var result = [];
        for (var i = 0; i < data.length; i++) {
          var geoCoord = geoCoordMap[data[i].name];
          if (geoCoord) {
            result.push({
              name: data[i].name,
              value: geoCoord.concat(data[i].value),
            });
          }
        }
        return result;
      };
      var option = {
        scale: 0.1,
        backgroundColor: "transparent",
        title: {
          text: "全国省市产品数据",
          subtext: "数据来自淘宝",
          left: "center",
          textStyle: {
            color: "#c0c0c0",
          },
        },
        geo: {
          show: true,
          map: "china",
          zoom: 1.25,
          label: {
            normal: {
              show: true,
              color: "white",
              fontSize: "8",
            },
            emphasis: {
              show: true,
              textStyle: {
                color: "white",
                fontSize: "10px",
              },
            },
          },
          roam: true,
          itemStyle: {
            normal: {
              areaColor: "skyblue",
              borderColor: "#fff",
            },
            emphasis: {
              areaColor: "#2b91b7",
            },
          },
        },
        series: [
          {
            name: "销量",
            type: "effectScatter",
            coordinateSystem: "geo",
            data: convertData(data),
            symbolSize: function(val) {
              return Math.max(6, val[2] / 10);
            },
            showEffectOn: "render",
            rippleEffect: {
              brushType: "stroke",
            },
            hoverAnimation: true,
            label: {
              formatter: "{b}",
              position: "right",
              show: true,
            },
            itemStyle: {
              color: "#ddb926",
            },
            emphasis: {
              label: {
                show: true,
              },
            }
          },
        ],
      };
      myChart.setOption(option);
    },

    drawRightTop() {
      var myChart = this.initChart('rightTopMain', 'rightTopChart');
      var option = {
        backgroundColor: "transparent",
        title: {
          text: "商品价格占比",
          left: "center",
          top: 28,
          textStyle: {
            color: "#c0c0c0",
            fontSize: 22,
            fontWeight: "bold"
          }
        },
        grid: {
          left: 56,
          right: 42,
          top: 92,
          bottom: 58
        },
        tooltip: {
          trigger: "axis"
        },
        legend: {
          data: ["占比情况"],
          top: 62,
          right: 34,
          textStyle: {
            color: "#c0c0c0"
          }
        },
        xAxis: {
          type: "category",
          data: this.realData.priceRangeList,
          axisLabel: {
            color: "#c0c0c0",
            fontSize: 12
          },
          axisLine: {
            lineStyle: {
              color: "#c0c0c0"
            }
          }
        },
        yAxis: {
          type: "value",
          axisLabel: {
            color: "#c0c0c0"
          },
          splitLine: {
            lineStyle: {
              color: "rgba(255,255,255,.55)"
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
      };
      myChart.setOption(option);
    },

    drawRightBottom() {
      var myChart = this.initChart('rightBottomMain', 'rightBottomChart');
      var dataList = this.realData.typeSalesList && this.realData.typeSalesList.length
        ? this.realData.typeSalesList
        : [{ name: "暂无数据", value: 0 }];
      var total = dataList.reduce(function(sum, item) {
        return sum + Number(item.value || 0);
      }, 0);
      var maxItem = dataList[0] || { name: "暂无数据", value: 0 };
      var percent = total > 0 ? Math.round((Number(maxItem.value || 0) / total) * 100) : 0;

      var option = {
        backgroundColor: "transparent",
        title: {
          text: "各类型销售量占比",
          left: "center",
          top: 22,
          textStyle: {
            color: "#c0c0c0",
            fontSize: 22,
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
            radius: ["42%", "65%"],
            center: ["50%", "58%"],
            data: dataList,
            label: {
              show: false
            },
            labelLine: {
              show: false
            },
            emphasis: {
              label: {
                show: false
              }
            }
          },
          {
            type: "pie",
            radius: ["0%", "0%"],
            center: ["50%", "58%"],
            silent: true,
            label: {
              show: true,
              position: "center",
              formatter: percent + "%\n" + maxItem.name,
              color: "#ffffff",
              fontSize: 24,
              lineHeight: 36
            },
            data: [{ value: 0, name: "" }]
          }
        ]
      };
      myChart.setOption(option);
    },

    drawAllCharts() {
      this.drawLeftTop();
      this.drawLeftBottom();
      this.drawCenterMap();
      this.drawRightTop();
      this.drawRightBottom();
    },

    changeData(x) {
      if (!Array.isArray(x) || x.length <= 1) return;
      var st = x[0];
      for (var i = 0; i < x.length - 1; i++) {
        x[i] = x[i + 1];
      }
      x[x.length - 1] = st;
    },

    updateBarChart() {
      if (this.isHovered === true && this.chart) {
        this.changeData(this.realData.cityList);
        this.changeData(this.realData.volumnList);
        this.chart.setOption({
          xAxis: {
            data: this.realData.cityList,
          },
          series: [
            {
              data: this.realData.volumnList
            },
          ],
        });
      }
    },

    startDataUpdataInterval() {
      const interval = 2000;
      clearInterval(this.timer);
      this.timer = setInterval(this.updateBarChart, interval);
    },

    startAction() {
      this.isHovered = false;
    },

    cancelAction() {
      this.isHovered = true;
    },

    handleResize() {
      if (this.chart) this.chart.resize();
      if (this.secondChart) this.secondChart.resize();
      if (this.mapChart) this.mapChart.resize();
      if (this.rightTopChart) this.rightTopChart.resize();
      if (this.rightBottomChart) this.rightBottomChart.resize();
    }
  },

  async mounted() {
    const res = await this.$http.get("myApp/screenData");
    const data = res.data || res;

    this.$set(this.realData, 'cityList', data.cityList || []);
    this.$set(this.realData, 'volumnList', data.volumnList || []);
    this.$set(this.realData, 'pieList', data.pieList || []);
    this.$set(this.realData, 'mapData', data.mapData || []);
    this.$set(this.realData, 'priceRangeList', data.priceRangeList || ["0-100", "100-200", "200-500", "500-1000", "千元以上"]);
    this.$set(this.realData, 'priceRangeValueList', data.priceRangeValueList || [0, 0, 0, 0, 0]);
    this.$set(this.realData, 'typeSalesList', data.typeSalesList || []);

    this.$nextTick(() => {
      this.drawAllCharts();
      this.startDataUpdataInterval();
    });

    window.addEventListener('resize', this.handleResize);
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize);
    clearInterval(this.timer);
    if (this.chart) this.chart.dispose();
    if (this.secondChart) this.secondChart.dispose();
    if (this.mapChart) this.mapChart.dispose();
    if (this.rightTopChart) this.rightTopChart.dispose();
    if (this.rightBottomChart) this.rightBottomChart.dispose();
  }
}
</script>

<style scoped>
/* 全局重置，让布局占满全屏 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

.layout {
  height: 100vh;
  width: 100%;
  background: url('../assets/imgs/bg.jpg') no-repeat center center;
  background-size: cover;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  height: 80px;
}

.header div {
  width: 50%;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.header div span {
  color: steelblue;
  font-weight: bold;
  font-size: 23px;
  padding: 10px;
}

/* 主要内容区域：flex 布局，子项默认拉伸高度 */
.content {
  flex: 1;
  display: flex;
  flex-direction: row;
  gap: 16px;
  padding: 16px;
  align-items: stretch;
  margin-top:80px
}

/* 左侧列：宽度随窗口缩放（基础宽度 25vw） */
.content .left {
  width: 25vw;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* 左侧两个盒子：宽度100%，高度按比例 380:298.24 计算 */
.content .left > div {
  width: 100%;
  height: calc(25vw * 298.24 / 380);
}

/* 右侧列：宽度按比例 350/380 相对于左列宽度 */
.content .right {
  width: calc(25vw * 350 / 380);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* 右侧两个盒子：宽度100%，高度按比例 350:298.24 计算，结果与左侧等高 */
.content .right > div {
  width: 100%;
  height: calc(25vw * 298.24 / 380);
}

/* 中间列：占据剩余宽度，高度由左/右列总高度决定（自动拉伸） */
.content .center {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* 中间内部 div 填满整个中间列的高度 */
.content .center > div {
  width: 100%;
  height: 100%;
}

/* 确保边框组件填满父容器，且内部内容正常显示 */
.dv-border-box-1,
.dv-border-box-8,
.dv-border-box-12,
.dv-border-box-13 {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 边框组件内部的直接 div 也占满 */
.dv-border-box-1 > div,
.dv-border-box-8 > div,
.dv-border-box-12 > div,
.dv-border-box-13 > div {
  flex: 1;
  width: 100%;
  height: 100%;
}

/* 响应式：窄屏时改为垂直排列，适当限制宽度避免溢出 */
@media (max-width: 800px) {
  .content {
    flex-direction: column;
    align-items: center;
  }
  .content .left,
  .content .right,
  .content .center {
    width: 80%;
    max-width: 500px;
  }
  .content .left > div,
  .content .right > div {
    height: auto;
    aspect-ratio: 380 / 298.24;
  }
  .content .right > div {
    aspect-ratio: 350 / 298.24;
  }
  .content .center {
    min-height: 300px;
  }
}
</style>