<template>
    <div class="login-vue" :style="bg">
        <div class="container">
            <p class="title">{{ isRegisterMode ? 'REGISTER' : 'WELCOME' }}</p>
            <div class="input-c">
                <Input prefix="ios-contact" v-model="account" placeholder="用户名" clearable @on-blur="verifyAccount" />
                <p class="error">{{accountError}}</p>
            </div>
            <div class="input-c">
                <Input type="password" v-model="pwd" prefix="md-lock" placeholder="密码" clearable @on-blur="verifyPwd" @keyup.enter.native="submit" />
                <p class="error">{{pwdError}}</p>
            </div>
            <div class="input-c" v-if="isRegisterMode">
                <Input type="password" v-model="confirmPwd" prefix="md-lock" placeholder="确认密码" clearable @on-blur="verifyConfirmPwd" @keyup.enter.native="submit" />
                <p class="error">{{confirmPwdError}}</p>
            </div>
            <Button :loading="isShowLoading" class="submit" type="primary" @click="submit">{{ isRegisterMode ? '注册' : '登录' }}</Button>
            <p class="account">
                <span @click="toggleMode">{{ isRegisterMode ? '返回登录' : '注册账号' }}</span>
                <template v-if="!isRegisterMode"> | <span @click="forgetPwd">忘记密码</span></template>
            </p>
        </div>
    </div>
</template>

<script>
export default {
    name: 'login',
    data() {
        return {
            isRegisterMode: false,
            account: '',
            pwd: '',
            confirmPwd: '',
            accountError: '',
            pwdError: '',
            confirmPwdError: '',
            isShowLoading: false,
            bg: {},
        }
    },
    created() {
        this.bg.backgroundImage = 'url(' + require('../assets/imgs/bg0' + new Date().getDay() + '.jpg') + ')'
    },
    watch: {
        $route: {
            handler(route) {
                this.redirect = route.query && route.query.redirect
            },
            immediate: true,
        },
    },
    methods: {
        verifyAccount() {
            if (!this.account) {
                this.accountError = '请输入用户名'
            } else if (this.account.length < 3) {
                this.accountError = '用户名至少3位'
            } else {
                this.accountError = ''
            }
        },
        verifyPwd() {
            if (!this.pwd) {
                this.pwdError = '请输入密码'
            } else if (this.pwd.length < 3) {
                this.pwdError = '密码至少3位'
            } else {
                this.pwdError = ''
            }
        },
        verifyConfirmPwd() {
            if (!this.isRegisterMode) {
                this.confirmPwdError = ''
                return
            }
            if (!this.confirmPwd) {
                this.confirmPwdError = '请确认密码'
            } else if (this.confirmPwd !== this.pwd) {
                this.confirmPwdError = '两次密码不一致'
            } else {
                this.confirmPwdError = ''
            }
        },
        validateForm() {
            this.verifyAccount()
            this.verifyPwd()
            this.verifyConfirmPwd()
            return !this.accountError && !this.pwdError && !this.confirmPwdError
        },
        toggleMode() {
            this.isRegisterMode = !this.isRegisterMode
            this.pwd = ''
            this.confirmPwd = ''
            this.accountError = ''
            this.pwdError = ''
            this.confirmPwdError = ''
        },
        forgetPwd() {
            this.$Message.info('登录后可在右上角菜单中修改密码')
        },
        saveLoginInfo(data) {
            const user = data.user || {}
            localStorage.setItem('userId', user.id || '')
            localStorage.setItem('userImg', 'https://avatars3.githubusercontent.com/u/22117876?s=460&v=4')
            localStorage.setItem('userName', user.username || this.account)
            localStorage.setItem('token', data.token || 'user_token')
        },
        async submit() {
            if (!this.validateForm()) return
            this.isShowLoading = true
            try {
                if (this.isRegisterMode) {
                    const res = await this.$http.post('myApp/register/', {
                        username: this.account,
                        password: this.pwd,
                        confirmPassword: this.confirmPwd,
                    })
                    const data = res.data || res
                    if (data.code === 0) {
                        this.$Message.success('注册成功，请登录')
                        this.isRegisterMode = false
                        this.pwd = ''
                        this.confirmPwd = ''
                    } else {
                        this.$Message.error(data.msg || '注册失败')
                    }
                } else {
                    const res = await this.$http.post('myApp/login/', {
                        username: this.account,
                        password: this.pwd,
                    })
                    const data = res.data || res
                    if (data.code === 0) {
                        this.saveLoginInfo(data.data || {})
                        this.$Message.success('登录成功')
                        this.$router.push({ path: this.redirect || '/' })
                    } else {
                        this.$Message.error(data.msg || '登录失败')
                    }
                }
            } catch (e) {
                this.$Message.error(this.isRegisterMode ? '注册接口请求失败' : '登录接口请求失败')
            } finally {
                this.isShowLoading = false
            }
        },
    },
}
</script>

<style>
.login-vue {
    height: 100%;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #fff;
    background-size: cover;
    background-position: center center;
}
.login-vue .container {
    background: rgba(255, 255, 255, .5);
    width: 320px;
    text-align: center;
    border-radius: 10px;
    padding: 30px;
}
.login-vue .ivu-input {
    background-color: transparent;
    color: #fff;
    outline: #fff;
    border-color: #fff;
}
.login-vue ::-webkit-input-placeholder {
    color: rgba(255, 255, 255, .8);
}
.login-vue :-moz-placeholder {
    color: rgba(255, 255, 255, .8);
}
.login-vue ::-moz-placeholder {
    color: rgba(255, 255, 255, .8);
}
.login-vue :-ms-input-placeholder {
    color: rgba(255, 255, 255, .8);
}
.login-vue .title {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 20px;
    letter-spacing: 1px;
}
.login-vue .input-c {
    margin: auto;
    width: 220px;
}
.login-vue .error {
    color: #ff3434;
    text-align: left;
    margin: 5px auto;
    font-size: 12px;
    padding-left: 30px;
    height: 20px;
}
.login-vue .submit {
    width: 220px;
}
.login-vue .account {
    margin-top: 24px;
}
.login-vue .account span {
    cursor: pointer;
}
.login-vue .ivu-icon {
    color: #eee;
}
.login-vue .ivu-icon-ios-close-circle {
    color: #777;
}
</style>
