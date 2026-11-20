<template>
  <KPage>
    <KSection>
      <KBlock>
        <KCell>
          <el-form :inline="true" @submit.prevent>
            <el-form-item label="兴趣关键词">
              <el-input  
                v-model="keyword" 
                placeholder="请输入兴趣关键词" 
                clearable 
                @keyup.enter="handleSearch" 
                style="width: 300px"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">查询</el-button>
            </el-form-item>
          </el-form>
        </KCell>
      </KBlock>
      <KBlock>
        <KCell>
          <el-table ref="tableRef" :data="tableData" border style="width: 100%" v-loading="loading" empty-text="暂无数据">
            
            <!-- 新增展开列，用于显示需求详情 -->
            <el-table-column type="expand">
              <template #default="props">
                <div style="padding: 10px 20px; background-color: #f9f9f9;">
                  <h4 style="margin: 0 0 10px 0; font-weight: bold;">发布的搭子需求：</h4>
                  <el-table :data="props.row.requests || []" border size="small" empty-text="该用户暂未发布需求">
                    <el-table-column prop="request_id" label="需求ID" width="100" align="center" />
                    <el-table-column prop="title" label="需求标题" />
                    <el-table-column prop="status" label="状态" width="120" align="center">
                      <template #default="{ row }">
                        <el-tag :type="row.status === 'open' ? 'success' : 'info'">{{ row.status }}</el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </template>
            </el-table-column>
             <!-- 新增展开列，用于显示需求详情 -->

            <el-table-column prop="user_id" label="用户ID" width="100" align="center" />
            <el-table-column prop="student_id" label="学号" width="150" align="center" />
            <el-table-column prop="username" label="用户名" width="150" align="center" />
            <el-table-column prop="phone" label="电话号码" width="150" align="center" />
            <el-table-column prop="email" label="邮箱" min-width="200" align="center" />
            <el-table-column prop="tags" label="个性标签" min-width="200" align="center" />
            
            <!-- 新增操作列，提示用户查看需求 -->
            <el-table-column label="发布需求" width="120" align="center">
              <template #default="{ row }">
                <el-button 
                  v-if="row.requests && row.requests.length > 0" 
                  link 
                  type="primary" 
                  @click="toggleExpand(row)"
                >
                  查看 ({{ row.requests.length }})
                </el-button>
                <span v-else style="color: #909399;">无</span>
              </template>
            </el-table-column>
          </el-table>
        </KCell>
      </KBlock>
    </KSection>
  </KPage>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { request } from "@kesplus/kesplus"

const keyword = ref('')
const tableData = ref([])
const loading = ref(false)
const tableRef = ref(null)

const toggleExpand = (row) => {
  tableRef.value.toggleRowExpansion(row)
}

const handleSearch = async () => {
  if (!keyword.value) {
    ElMessage.warning('请输入兴趣关键词')
    return
  }

  loading.value = true
  try {
    // 调用后端函数 searchUsersByInterest
    // 参数 p_keyword 对应 SQL 函数的参数名
    const response = await request.get('/user_management/searchUsersByInterest', {
      params: {
        p_keyword: keyword.value
      }
    })

    console.log('API Response:', response)

    // 兼容处理响应数据
    let data = response
    if (response && response.data) {
        data = response.data
    }
    
    if (Array.isArray(data)) {
        tableData.value = data
        if (data.length === 0) {
            ElMessage.info('未找到匹配的用户')
        } else {
            ElMessage.success(`查询成功，共找到 ${data.length} 位用户`)
        }
    } else {
        // 如果返回的是空或者其他非数组结构，重置为空数组
        tableData.value = []
        if (data) {
             // 如果 data 有值但不是数组，可能是单个对象，尝试放入数组
             tableData.value = [data]
        } else {
             ElMessage.info('未找到匹配的用户')
        }
    }

  } catch (error) {
    console.error(error)
    ElMessage.error('查询失败，请检查网络或权限')
    tableData.value = []
  } finally {
    loading.value = false
  }
}
</script>
