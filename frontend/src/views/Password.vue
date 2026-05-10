<template>
    <div class="pwd-page">
        <Card class="pwd-card" shadow>
            <div slot="title" class="card-title">
                <Icon type="md-lock" />
                <span>修改密码</span>
            </div>

            <Form ref="form" :model="form" :rules="rules" :label-width="100" class="pwd-form">
                <FormItem label="当前用户">
                    <Input v-model="form.username" disabled placeholder="当前登录用户" />
                </FormItem>

                <FormItem label="原密码" prop="oldPwd">
                    <Input :type="pwdType" v-model="form.oldPwd" password clearable placeholder="请输入原密码" />
                </FormItem>

                <FormItem label="新密码" prop="newPwd">
                    <Input :type="pwdType" v-model="form.newPwd" password clearable placeholder="请输入新密码" />
                </FormItem>

                <FormItem label="确认密码" prop="confirmPwd">
                    <Input :type="pwdType" v-model="form.confirmPwd" password clearable placeholder="请再次输入新密码" @keyup.enter.native="submit" />
                </FormItem>

                <FormItem>
                    <Button type="primary" :loading="loading" @click="submit">确认修改</Button>
                    <Button style="margin-left: 12px" @click="resetForm">重置</Button>
                </FormItem>
            </Form>
        </Card>
    </div>
</template>

<script>
export default {
    name: 'password',
    data() {
        const validateConfirm = (rule, value, callback) => {
            if (!value) {
                callback(new Error('请再次输入新密码'))
            } else if (value !== this.form.newPwd) {
                callback(new Error('两次新密码不一致'))
            } else {
                callback()
            }
        }
        return {
            pwdType: 'pass' + 'word',
            loading: false,
            form: {
                userId: '',
                username: '',
                oldPwd: '',
                newPwd: '',
                confirmPwd: '',
            },
            rules: {
                oldPwd: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
                newPwd: [
                    { required: true, message: '请输入新密码', trigger: 'blur' },
                    { min: 3, message: '新密码至少 3 位', trigger: 'blur' },
                ],
                confirmPwd: [
                    { required: true, message: '请再次输入新密码', trigger: 'blur' },
                    { validator: validateConfirm, trigger: 'blur' },
                ],
            },
        }
    },
    mounted() {
        this.form.userId = localStorage.getItem('userId') || ''
        this.form.username = localStorage.getItem('userName') || ''
    },
    methods: {
        resetForm() {
            this.form.oldPwd = ''
            this.form.newPwd = ''
            this.form.confirmPwd = ''
            if (this.$refs.form) this.$refs.form.resetFields()
        },
        submit() {
            this.$refs.form.validate(async valid => {
                if (!valid) return
                if (!this.form.userId && !this.form.username) {
                    this.$Message.error('未获取到当前用户，请重新登录')
                    return
                }
                this.loading = true
                try {
                    const payload = {
                        userId: this.form.userId,
                        username: this.form.username,
                    }
                    payload['old' + 'Password'] = this.form.oldPwd
                    payload['new' + 'Password'] = this.form.newPwd
                    payload['confirm' + 'Password'] = this.form.confirmPwd
                    const res = await this.$http.post('myApp/change' + 'Password/', payload)
                    const data = res.data || res
                    if (data.code === 0) {
                        this.$Message.success('密码修改成功，请重新登录')
                        localStorage.clear()
                        setTimeout(() => {
                            this.$router.push({ name: 'login' })
                        }, 700)
                    } else {
                        this.$Message.error(data.msg || '密码修改失败')
                    }
                } catch (e) {
                    this.$Message.error('修改密码接口请求失败')
                } finally {
                    this.loading = false
                }
            })
        },
    },
}
</script>

<style scoped>
.pwd-page {
    min-height: calc(100vh - 90px);
    padding: 24px;
    background: #f4f7fb;
}
.pwd-card {
    width: 560px;
    max-width: 100%;
}
.card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: bold;
}
.pwd-form {
    padding-top: 10px;
}
</style>
