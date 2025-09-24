import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Bot,
  LayoutDashboard,
  Play,
  FileText,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  User,
  Zap
} from 'lucide-react'

const Sidebar = ({ open, onToggle, user, onLogout }) => {
  const location = useLocation()

  const menuItems = [
    {
      path: '/dashboard',
      icon: LayoutDashboard,
      label: 'Dashboard',
      description: 'Overview & Analytics'
    },
    {
      path: '/applications',
      icon: Bot,
      label: 'Applications',
      description: 'Manage Your Apps'
    },
    {
      path: '/create-test',
      icon: Zap,
      label: 'Create Tests',
      description: 'AI-Powered Test Creation'
    },
    {
      path: '/results',
      icon: FileText,
      label: 'Test Results',
      description: 'View Test Reports'
    },
    {
      path: '/requirements',
      icon: Settings,
      label: 'Templates',
      description: 'Manage Templates'
    },
    {
      path: '/settings',
      icon: Settings,
      label: 'Settings',
      description: 'Account & Preferences'
    }
  ]

  const isActive = (path) => location.pathname === path

  return (
    <motion.aside
      initial={false}
      animate={{ width: open ? 256 : 64 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="fixed left-0 top-0 h-screen bg-sidebar border-r border-sidebar-border z-50 flex flex-col"
    >
      {/* Header */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between">
          <motion.div
            initial={false}
            animate={{ opacity: open ? 1 : 0 }}
            transition={{ duration: 0.2 }}
            className="flex items-center gap-3"
          >
            <div className="relative">
              <Bot className="w-8 h-8 text-sidebar-primary" />
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                className="absolute -top-1 -right-1"
              >
                <Zap className="w-4 h-4 text-chart-1" />
              </motion.div>
            </div>
            {open && (
              <div>
                <h1 className="font-bold text-sidebar-foreground">AI Test Automation</h1>
                <p className="text-xs text-sidebar-foreground/70">SaaS Platform</p>
              </div>
            )}
          </motion.div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="text-sidebar-foreground hover:bg-sidebar-accent"
          >
            {open ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.path)
          
          return (
            <Link key={item.path} to={item.path}>
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`relative flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  active
                    ? 'bg-sidebar-primary text-sidebar-primary-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                }`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                
                <motion.div
                  initial={false}
                  animate={{ opacity: open ? 1 : 0, width: open ? 'auto' : 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="font-medium">{item.label}</div>
                  <div className="text-xs opacity-70">{item.description}</div>
                </motion.div>

                {active && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="absolute left-0 top-0 bottom-0 w-1 bg-sidebar-primary-foreground rounded-r"
                  />
                )}
              </motion.div>
            </Link>
          )
        })}
      </nav>

      {/* User Profile */}
      <div className="p-4 border-t border-sidebar-border">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 p-3 h-auto text-sidebar-foreground hover:bg-sidebar-accent"
            >
              <Avatar className="w-8 h-8">
                <AvatarFallback className="bg-sidebar-primary text-sidebar-primary-foreground">
                  {user?.username?.[0]?.toUpperCase() || 'U'}
                </AvatarFallback>
              </Avatar>
              
              <motion.div
                initial={false}
                animate={{ opacity: open ? 1 : 0, width: open ? 'auto' : 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden text-left"
              >
                <div className="font-medium">{user?.username}</div>
                <div className="text-xs opacity-70 flex items-center gap-1">
                  <Badge variant="secondary" className="text-xs px-1">
                    {user?.api_usage || 0}/{user?.api_quota || 0}
                  </Badge>
                  API calls
                </div>
              </motion.div>
            </Button>
          </DropdownMenuTrigger>
          
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuItem>
              <User className="w-4 h-4 mr-2" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={onLogout} className="text-destructive">
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </motion.aside>
  )
}

export default Sidebar
