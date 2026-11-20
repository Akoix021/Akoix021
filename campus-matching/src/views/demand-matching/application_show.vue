<template>
  <KPage    >
    <KSection>
      <KBlock>
        <KCell>
          <el-form ref="formRef" label-width="auto" :model="form">
            <KRow>
              <KCell>
                <el-form-item label="申请ID">
                  <!-- 1. 绑定 v-model 到 applicationID -->
                  <el-input v-model="applicationID" placeholder="请输入申请ID" />
                  <el-button  @click="queryApplicationStatus" type="primary"  style="margin-left:10px;">
                    <el-text>查询</el-text>
                  </el-button>
                </el-form-item>
              </KCell>
            </KRow>
          </el-form>
        </KCell>
      </KBlock>
      <KBlock>
        <KCell>
          <!-- 3. 使用 el-table 展示数据 -->
          <el-table :data="tableData" border style="width: 100%">
            <el-table-column prop="application_id" label="申请ID" />
            <el-table-column prop="application_status" label="申请状态" />
            <el-table-column prop="request_status" label="需求状态" />
            <el-table-column prop="remaining_slots" label="剩余名额" />
          </el-table>
        </KCell>
      </KBlock>
    </KSection>
  </KPage>
</template>
<script setup>

import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { request } from "@kesplus/kesplus"

const form = reactive({})
const applicationID = ref('') // 存储用户输入的申请ID
const tableData = ref([]) // 存储表格数据

const queryApplicationStatus = async () => {
  if (!applicationID.value) {
    ElMessage.warning('请输入申请ID！')
    return
  }

  try {
    // 4. 发送 GET 请求调用后端函数
    // 注意：URL 需要根据实际配置的 RESTful 接口地址调整
    // 参数名 p_application_id 需与后端函数参数名一致
    const response = await request.get('/demand_matching/queryApplicationStatus', {
      params: {
        p_application_id: applicationID.value
      }
    })

    // 5. 处理响应
    console.log('API Response:', response)
    
    // 兼容不同的响应结构
    // 1. 如果 response 本身就是数据对象 (KES Plus 常见情况)
    // 2. 如果 response.data 是数据对象
    let data = response
    if (response && response.data) {
        data = response.data
    }

    if (data && (data.application_id !== undefined || Object.keys(data).length > 0)) {
      // 确保 data 是对象而不是空对象
      if (Object.keys(data).length === 0) {
         tableData.value = []
         ElMessage.warning('未找到该申请ID的信息')
      } else {
         tableData.value = [data]
         ElMessage.success('查询成功')
      }
    } else {
      tableData.value = []
      ElMessage.warning('未找到该申请ID的信息')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('查询失败，请检查网络或权限')
    tableData.value = []
  }
}

</script>