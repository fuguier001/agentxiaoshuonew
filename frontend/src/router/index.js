import { createRouter, createWebHistory } from 'vue-router'

const Dashboard = () => import('../views/Dashboard.vue')
const AutoCreation = () => import('../views/AutoCreation.vue')
const NovelLibrary = () => import('../views/NovelLibrary.vue')
const ProjectConfig = () => import('../views/ProjectConfig.vue')
const AgentMonitor = () => import('../views/AgentMonitor.vue')
const WritingPanel = () => import('../views/WritingPanel.vue')
const LearningPanel = () => import('../views/LearningPanel.vue')
const SchoolRegistry = () => import('../views/SchoolRegistry.vue')
const Trash = () => import('../views/Trash.vue')

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'dashboard', component: Dashboard },
  { path: '/auto', name: 'auto', component: AutoCreation },
  { path: '/library', name: 'library', component: NovelLibrary },
  { path: '/trash', name: 'trash', component: Trash },
  { path: '/config', name: 'config', component: ProjectConfig },
  { path: '/monitor', name: 'monitor', component: AgentMonitor },
  { path: '/writing', name: 'writing', component: WritingPanel },
  { path: '/learning', name: 'learning', component: LearningPanel },
  { path: '/schools', name: 'schools', component: SchoolRegistry },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
