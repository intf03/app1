<template>
    <div class="data-source-page">
        <div class="data-card">
            <div class="page-title">商品数据来源</div>
            <div class="query-bar">
                <Input
                    v-model="query.keyword"
                    search
                    clearable
                    placeholder="请输入商品名称、店铺、类型或地区"
                    style="width: 320px"
                    @on-search="handleSearch"
                    @on-clear="handleSearch"
                />
                <Select v-model="query.type" clearable placeholder="商品类型" style="width: 160px" @on-change="handleSearch">
                    <Option v-for="item in typeList" :key="item" :value="item">{{ item }}</Option>
                </Select>
                <Select v-model="query.address" clearable placeholder="地区" style="width: 160px" @on-change="handleSearch">
                    <Option v-for="item in addressList" :key="item" :value="item">{{ item }}</Option>
                </Select>
                <Button type="primary" @click="handleSearch">查询</Button>
                <Button @click="resetSearch">重置</Button>
            </div>

            <Table
                border
                stripe
                :loading="loading"
                :columns="columns"
                :data="tableData"
                max-height="620"
            ></Table>

            <div class="pager-wrap">
                <Page
                    :total="total"
                    :current="query.page"
                    :page-size="query.pageSize"
                    show-sizer
                    show-elevator
                    show-total
                    @on-change="handlePageChange"
                    @on-page-size-change="handlePageSizeChange"
                />
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'DataSource',
    data() {
        return {
            loading: false,
            query: {
                page: 1,
                pageSize: 10,
                keyword: '',
                type: '',
                address: '',
            },
            total: 0,
            tableData: [],
            typeList: [],
            addressList: [],
            columns: [
                {
                    title: '序号',
                    width: 70,
                    align: 'center',
                    render: (h, params) => h('span', (this.query.page - 1) * this.query.pageSize + params.index + 1),
                },
                {
                    title: '商品图片',
                    key: 'img_src',
                    width: 110,
                    align: 'center',
                    render: (h, params) => {
                        const src = params.row.img_src
                        const href = params.row.href
                        if (!src) return h('span', '无')

                        const imageNode = h('img', {
                            attrs: {
                                src,
                                alt: params.row.title || '商品图片',
                                title: href ? '点击查看商品详情' : '暂无商品链接',
                            },
                            style: {
                                width: '54px',
                                height: '54px',
                                objectFit: 'cover',
                                borderRadius: '6px',
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
                },
                {
                    title: '商品名称',
                    key: 'title',
                    minWidth: 260,
                    tooltip: true,
                },
                {
                    title: '类型',
                    key: 'type',
                    width: 120,
                    align: 'center',
                },
                {
                    title: '价格',
                    key: 'price',
                    width: 120,
                    align: 'center',
                    render: (h, params) => h('span', params.row.price ? `￥${params.row.price}` : '-'),
                },
                {
                    title: '销量',
                    key: 'buy_len',
                    width: 120,
                    align: 'center',
                },
                {
                    title: '店铺',
                    key: 'name',
                    minWidth: 160,
                    tooltip: true,
                },
                {
                    title: '地区',
                    key: 'address',
                    width: 130,
                    align: 'center',
                },
                {
                    title: '是否包邮',
                    key: 'isFreeDelivery',
                    width: 120,
                    align: 'center',
                },
                {
                    title: '链接',
                    width: 90,
                    align: 'center',
                    render: (h, params) => {
                        if (!params.row.href) return h('span', '-')
                        return h('a', {
                            attrs: {
                                href: params.row.href,
                                target: '_blank',
                                rel: 'noopener noreferrer',
                            },
                        }, '查看')
                    },
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
                const data = res.data || res
                if (data.code === 0 || Array.isArray(data.data)) {
                    this.tableData = data.data || []
                    this.total = data.total || this.tableData.length || 0
                    this.typeList = data.typeList || []
                    this.addressList = data.addressList || []
                } else {
                    this.$Message.error(data.msg || '数据加载失败')
                }
            } catch (e) {
                this.$Message.error('数据来源接口请求失败')
            } finally {
                this.loading = false
            }
        },
        handleSearch() {
            this.query.page = 1
            this.fetchData()
        },
        resetSearch() {
            this.query.keyword = ''
            this.query.type = ''
            this.query.address = ''
            this.query.page = 1
            this.fetchData()
        },
        handlePageChange(page) {
            this.query.page = page
            this.fetchData()
        },
        handlePageSizeChange(pageSize) {
            this.query.pageSize = pageSize
            this.query.page = 1
            this.fetchData()
        },
    },
}
</script>

<style scoped>
.data-source-page {
    min-height: calc(100vh - 90px);
    padding: 18px;
    background: #f4f7fb;
}

.data-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, .06);
}

.page-title {
    font-size: 22px;
    font-weight: bold;
    color: #17233d;
    margin-bottom: 18px;
}

.query-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    margin-bottom: 16px;
}

.pager-wrap {
    margin-top: 16px;
    display: flex;
    justify-content: flex-end;
}
</style>
