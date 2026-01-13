import React, { useState, useEffect } from 'react';

const NotificationsPanel = ({ isVisible = true }) => {
  const [notifications, setNotifications] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    // Mock notifications for demonstration
    const mockNotifications = [
      {
        id: 1,
        type: 'info',
        title: 'Council Sync Complete',
        message: 'All cores synchronized successfully',
        timestamp: new Date(Date.now() - 300000), // 5 minutes ago
        read: false
      },
      {
        id: 2,
        type: 'warning',
        title: 'High Memory Usage',
        message: 'Cali X memory usage at 89%',
        timestamp: new Date(Date.now() - 600000), // 10 minutes ago
        read: false
      },
      {
        id: 3,
        type: 'success',
        title: 'Model Training Complete',
        message: 'KayGee neural network updated',
        timestamp: new Date(Date.now() - 900000), // 15 minutes ago
        read: true
      },
      {
        id: 4,
        type: 'error',
        title: 'Connection Lost',
        message: 'Brief disconnect from Caleon core',
        timestamp: new Date(Date.now() - 1200000), // 20 minutes ago
        read: true
      }
    ];

    setNotifications(mockNotifications);
  }, []);

  const getTypeStyles = (type) => {
    switch (type) {
      case 'success':
        return 'border-green-500 bg-green-900/20';
      case 'warning':
        return 'border-yellow-500 bg-yellow-900/20';
      case 'error':
        return 'border-red-500 bg-red-900/20';
      default:
        return 'border-blue-500 bg-blue-900/20';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      default: return 'ℹ️';
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  const formatTime = (date) => {
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  if (!isVisible) return null;

  return (
    <div className="fixed top-20 right-6 z-40">
      {/* Notification Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="relative bg-gray-800 hover:bg-gray-700 p-3 rounded-full shadow-lg transition"
      >
        🔔
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {/* Notifications Panel */}
      {isExpanded && (
        <div className="absolute top-16 right-0 w-96 bg-gray-800 rounded-lg shadow-xl border border-gray-700 max-h-96 overflow-hidden">
          <div className="p-4 border-b border-gray-700">
            <div className="flex justify-between items-center">
              <h3 className="font-bold">Notifications</h3>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-400">
                No notifications
              </div>
            ) : (
              notifications.map(notification => (
                <div
                  key={notification.id}
                  className={`p-4 border-l-4 ${getTypeStyles(notification.type)} ${
                    !notification.read ? 'bg-gray-700/50' : ''
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-lg">{getTypeIcon(notification.type)}</span>
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <h4 className="font-bold text-sm">{notification.title}</h4>
                        <span className="text-xs text-gray-400">
                          {formatTime(notification.timestamp)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-300 mt-1">{notification.message}</p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="p-3 border-t border-gray-700 bg-gray-900">
            <button className="w-full text-center text-sm text-cyan-400 hover:text-cyan-300">
              View All Notifications
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationsPanel;