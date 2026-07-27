/**
 * GoalFit-AI Pro Web Push Notification Engine
 * Handles native Desktop & Mobile Phone Browser Push Notifications
 */

window.requestPushPermission = function() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                console.log("Push notifications enabled!");
            }
        });
    }
};

// Fire on initial load
if ('Notification' in window && Notification.permission === 'default') {
    window.requestPushPermission();
}

let lastTriggeredMinute = '';

async function checkScheduledReminders() {
    if (!('Notification' in window) || Notification.permission !== 'granted') return;

    const now = new Date();
    const currentMin = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

    if (currentMin === lastTriggeredMinute) return; // avoid duplicate triggers in same minute

    try {
        const res = await fetch('/user/reminders/');
        if (!res.ok) return;
        const data = await res.json();

        if (!data || !data.enable_push) return;

        const reminders = [
            { time: data.breakfast_time, title: "🌅 Breakfast Reminder", body: "It's time for your scheduled Breakfast! Don't forget to log your meal." },
            { time: data.lunch_time, title: "🥗 Lunch Reminder", body: "It's time for Lunch! Fuel your body and track your macros." },
            { time: data.snack_time, title: "🍎 Snack Reminder", body: "Time for a healthy snack break! Keep your energy up." },
            { time: data.dinner_time, title: "🍲 Dinner Reminder", body: "Time for Dinner! Stay on track with your daily nutrition targets." },
            { time: data.workout_time, title: "🏋️ Workout Time!", body: "Time for your daily fitness routine! Ready to crush your goals?" }
        ];

        reminders.forEach(item => {
            if (item.time && item.time === currentMin) {
                lastTriggeredMinute = currentMin;
                new Notification(item.title, {
                    body: item.body,
                    icon: '/static/images/logo.png',
                    badge: '/static/images/logo.png',
                    tag: item.title
                });
            }
        });

    } catch (e) {
        console.error("Error checking reminders", e);
    }
}

// Check every 30 seconds for scheduled times
setInterval(checkScheduledReminders, 30000);
