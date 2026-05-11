<template>
    <div class="overview-page">
        <div class="section-card condition-card">
            <div class="section-title">▦ 条件选择</div>
            <div class="condition-body">
                <div class="condition-item">
                    <span class="dash">-</span>
                    <div class="field-wrap">
                        <div class="field-label">地址</div>
                        <Select v-model="query.address" clearable placeholder="请选择" style="width: 190px">
                            <Option v-for="item in addressList" :key="item" :value="item">{{ item }}</Option>
                        </Select>
                    </div>
                </div>

                <div class="condition-item">
                    <span class="dash">-</span>
                    <div class="field-wrap">
                        <div class="field-label">产品类型</div>
                        <Select v-model="query.type" clearable placeholder="请选择" style="width: 190px">
                            <Option v-for="item in typeList" :key="item" :value="item">{{ item }}</Option>
                        </Select>
                    </div>
                </div>

                <Button type="primary" class="submit-btn" :loading="loading" @click="handleSearch">提交</Button>
            </div>
        </div>

        <div class="section-card data-card">
            <div class="section-title">▣ 数据</div>
            <div class="table-shell">
                <Table
                    border
                    stripe
                    :loading="loading"
                    :columns="columns"
                    :data="tableData"
                    height="365"
                ></Table>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'OverviewTable',
    data() {
        return {
            loading: false,
            query: {
                page: 1,
                pageSize: 200,
                type: '',
                address: '',
            },
            tableData: [],
            typeList: [],
            addressList: [],
            columns: [
                {
                    title: '商品导入序号',
                    width: 120,
                    align: 'center',
                    render: (h, params) => h('span', this.getRowId(params.row, params.index)),
                },
                {
                    title: '类型',
                    key: 'type',
                    width: 110,
                    align: 'center',
                },
                {
                    title: '商品名',
                    key: 'title',
                    minWidth: 360,
                    align: 'center',
                    tooltip: true,
                },
                {
                    title: '销量',
                    key: 'buy_len',
                    width: 110,
                    align: 'center',
                },
                {
                    title: '图片',
                    key: 'img_src',
                    width: 180,
                    align: 'center',
                    render: (h, params) => this.renderProductImage(h, params.row),
                },
                {
                    title: '店铺',
                    key: 'name',
                    minWidth: 210,
                    align: 'center',
                    tooltip: true,
                },
                {
                    title: '地址',
                    key: 'address',
                    width: 140,
                    align: 'center',
                },
                {
                    title: '是否包邮',
                    key: 'isFreeDelivery',
                    width: 130,
                    align: 'center',
                    render: (h, params) => h('span', this.formatDelivery(params.row.isFreeDelivery)),
                },
            ],
        }
    },
    mounted() {
        this.fetchData()
    },
    methods: {
        async fetchData() {
            this.loading = true
            try {
                const res = await this.$http.get('myApp/productList', {
                    params: this.query,
                })
                const body = res.data || res
                if (body.code === 0 || Array.isArray(body.data)) {
                    this.tableData = body.data || []
                    this.typeList = body.typeList || this.getUniqueList(this.tableData, 'type')
                    this.addressList = body.addressList || this.getUniqueList(this.tableData, 'address')
                } else {
                    this.$Message.error(body.msg || '数据加载失败')
                }
            } catch (e) {
                this.$Message.error('总览数据接口请求失败')
            } finally {
                this.loading = false
            }
        },
        handleSearch() {
            this.query.page = 1
            this.fetchData()
        },
        getUniqueList(list, key) {
            return Array.from(new Set((list || []).map(item => item && item[key]).filter(Boolean)))
        },
        getRowId(row, index) {
            return row.id || row.product_id || row.goods_id || row.item_id || index + 1
        },
        renderProductImage(h, row) {
            const src = row.img_src
            const href = row.href
            if (!src) return h('span', '-')

            const imageNode = h('img', {
                attrs: {
                    src,
                    alt: row.title || '商品图片',
                    title: href ? '点击查看商品详情' : '暂无商品链接',
                },
                style: {
                    width: '82px',
                    height: '82px',
                    objectFit: 'cover',
                    cursor: href ? 'pointer' : 'default',
                    verticalAlign: 'middle',
                },
            })

            if (!href) return imageNode
            return h('a', {
                attrs: {
                    href,
                    target: '_blank',
                    rel: 'noopener noreferrer',
                },
                style: {
                    display: 'inline-block',
                    lineHeight: 0,
                },
            }, [imageNode])
        },
        formatDelivery(value) {
            if (value === 1 || value === '1' || value === true || value === 'true' || value === '包邮') return '1'
            if (value === 0 || value === '0' || value === false || value === 'false' || value === '不包邮') return '0'
            return value || '-'
        },
    },
}
</script>

<style scoped>
.overview-page {
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

.table-shell {
    margin: 20px;
    border: 1px solid #dcdee2;
    border-radius: 5px;
    overflow: hidden;
}

::v-deep .ivu-table td {
    height: 112px;
    font-size: 15px;
    color: #666;
}

::v-deep .ivu-table th {
    height: 48px;
    font-size: 15px;
    color: #333;
    font-weight: 500;
    background: #fff;
}
</style>
