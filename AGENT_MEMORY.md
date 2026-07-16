# GoalFit AI Pro - Professional Portal Memory

## Professional Architecture
- **Blueprints Structure**: Separated into `pro_bp` (Dashboard), `pro_diet_bp`, `pro_workout_bp`, `pro_transformations_bp`, `pro_schedule_bp`, `pro_earnings_bp` for a modular professional portal.
- **Authentication**: Isolated professional authentication flows in `professional_auth.py` via `/professional/login` and `/professional/register`.
- **Authorization**: Custom `@pro_required` decorator ensures only valid professionals can access `/pro/*` routes.
- **Role Logic**: Dieticians see `Create Meal` / `Create Diet Plan`. Trainers see `Add Exercise` / `Create Workout Plan`. 'Both' sees all.

## UI Decisions
- **Premium SaaS Theme**: The professional portal uses `professional.css` featuring dark mode, glassmorphism, accent glows (`var(--pro-primary)`, `var(--pro-accent)`), and smooth animations (`data-aos`).
- **Sidebar Navigation**: Dedicated `pro_base.html` providing a completely distinct look from the client side. Includes expandable submenus for Diet and Workout modules.
- **Dashboard Widgets**: Includes "Revenue Analytics" chart, "Client Distribution" donut chart, recent payment lists, pending client requests, and role-specific "Quick Actions" to add items to libraries.
- **Forms**: Clean, card-based `pro-card` forms for building meals and workouts.

## Database Additions
- `professional_meals`: `id, professional_id, meal_name, calories, protein, carbs, fats, ingredients, instructions, image`
- `professional_workouts`: `id, professional_id, workout_name, target_muscle, sets, reps, rest_time, instructions`
- `custom_diet_plans`, `custom_diet_plan_meals`: Tables linking professional-assigned plans to clients.
- `custom_workout_plans`, `custom_workout_plan_exercises`: Tables linking professional-assigned regimens to clients.

## Workflows Completed
- **Dashboard View**: Full metrics aggregation.
- **Client Management**: Listing active/pending/completed clients and detailed profile viewing.
- **Diet Management**: Creating meals, managing meal library, building custom plans from the library, and assigning to active clients.
- **Workout Management**: Adding exercises, managing exercise library, building custom weekly splits, and assigning to active clients.
- **Quick Actions**: Added a "Quick Add" dropdown menu in the professional topbar to allow instant addition of meals, exercises, and transformations to the professional's library from any page.
- **User Side Reflection**: User "My Professionals" dashboard (`/marketplace/my-professionals`) tracks active hired coaches, and standard AI generation is hidden when assigned a "Hybrid" coach.

## Next Steps / Pending Features
- **File Uploads**: Implement actual file saving logic for Transformation photos, Profile updates, and custom Meal/Exercise thumbnails.
- **Payments UI Integration**: Connect the actual payout tracking to Razorpay webhooks.
- **Scheduling/Appointments Logic**: Build the date/time picker logic for booking consultations.
