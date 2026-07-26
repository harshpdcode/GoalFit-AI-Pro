# GoalFit AI Pro — Project Report Documentation

**(Format: 3rd Semester MSc IT — Software Project II [IOM6043C])**

---

# [Title Page] (Page i)

<br>

<div align="center">

# A PROJECT REPORT ON

# **GOALFIT AI PRO**

**(AI-Based Personalised Fitness & Nutrition Platform with Professional Marketplace)**

<br>

_Submitted to_

### **The Department of Computer Science**

<br>

_In Partial fulfilment of the requirements for the 3rd Semester Project of_

### **MASTER OF SCIENCE INFORMATION TECHNOLOGY (MSc IT)**

### **Software Project II (IOM6043C)**

### **Academic Year: 2026-2027**

<br>

**Silver Oak College of Computer Application**  
**Department of Computer Science**  
**Silver Oak University, Ahmedabad, Gujarat**

<br>

| Submitted By:                    | Guided By:                |
| :------------------------------- | :------------------------ |
| **Pandya Harsh** (2504070200015) | **Mr. Ketan Nakum**       |
|                                  | **Asst. Prof. SoCA, SOU** |

</div>

---

<br>

# CERTIFICATE (Page ii)

<div align="right">
<b>Date:</b> ______________
</div>

<br>

This is to certify that the project entitled **“GOALFIT AI PRO”** has been carried out by **Pandya Harsh (Enrol. No. 2504070200015)**, **Chudasama Shakshiba Mahendrasinh (Enrol. No. 2504070200003)**, **Bhojak Hetul Chetanbhai (Enrol. No. 2504070200021)**, **Panchal Nisha Vipulbhai (Enrol. No. 2504070200028)**, and **Desai Archi Ghanshyambhai (Enrol. No. 2504070200075)** under the guidance of **Ms. Kamini Patel** in fulfillment of the 3rd Semester **Software Project II (IOM6043C)** at Silver Oak College of Computer Application, Silver Oak University, Ahmedabad during academic year 2026-2027.

<br><br><br>

|                                  |                       |                                |
| :------------------------------- | :-------------------: | -----------------------------: |
| **Internal Guide**               | **External Examiner** |         **Head of Department** |
| Ms. Kamini Patel                 |                       | Department of Computer Science |
| Assistant Professor, Dept. of CS |                       |          Silver Oak University |

---

<br>

# STUDENT DECLARATION (Page iii)

We hereby declare that the project entitled **"GOALFIT AI PRO"** submitted in partial fulfilment of the requirements for the 3rd Semester of **Master Of Science Information Technology (MSc IT)** is an original work carried out by us under the guidance of **Ms. Kamini Patel**.

We further declare that this project report, or any part thereof, has not been submitted by us or any other person for the award of any other degree or diploma of this or any other university.

We also declare that all the information furnished in this project report is based on our own study, analysis, and implementation, and due acknowledgement has been made wherever the work of others has been referred to.

<br>

**Place:** Ahmedabad  
**Date:** **\*\***\_\_**\*\***

<br>

<div align="right">

**Signature of the Students:**

1. \***\*\*\*\*\***\_\_\***\*\*\*\*\*** (Pandya Harsh - 2504070200015)
2. \***\*\*\*\*\***\_\_\***\*\*\*\*\*** (Chudasama Shakshiba M. - 2504070200003)
3. \***\*\*\*\*\***\_\_\***\*\*\*\*\*** (Bhojak Hetul Chetanbhai - 2504070200021)
4. \***\*\*\*\*\***\_\_\***\*\*\*\*\*** (Panchal Nisha Vipulbhai - 2504070200028)
5. \***\*\*\*\*\***\_\_\***\*\*\*\*\*** (Desai Archi Ghanshyambhai - 2504070200075)

</div>

---

<br>

# ACKNOWLEDGMENT (Page iv)

The development of **GoalFit AI Pro** was a collaborative undertaking, and we are deeply grateful to all who contributed to its successful completion.

We extend our sincere appreciation to **Ms. Kamini Patel** for her invaluable guidance, support, and expertise throughout this project. Her insightful feedback and direction were instrumental in shaping the system's design, modular architecture, and functionality.

We are also grateful to the **Department of Computer Science, Silver Oak College of Computer Application**, for providing the essential resources and infrastructure that made the development of **GoalFit AI Pro** possible. Their support was invaluable.

Furthermore, we would like to thank the fitness enthusiasts, independent trainers, and dieticians who generously participated in the requirement-gathering and testing phases. Their feedback was crucial in identifying areas for improvement and ensuring the system effectively addresses the real-world demands of personalized health management.

This project would not have been possible without the collective efforts of everyone involved. We are truly grateful for their contributions and unwavering support.

<br>

<div align="right">
<b>Group No. 4</b><br>
MSc IT Semester 3<br>
Silver Oak University
</div>

---

<br>

# ABSTRACT (Page v)

**GoalFit AI Pro** is a comprehensive, full-stack web application developed to modernize health tracking, nutrition management, and personal fitness coaching into an automated, user-friendly digital ecosystem. The system replaces generic, fragmented fitness tools with a unified platform that combines rule-based AI algorithms for diet and workout personalization alongside an interactive marketplace where users can hire verified personal trainers and dieticians.

Developed using Python (Flask), MySQL, HTML5, CSS3, and JavaScript, the system follows a modular architecture structured across **27 specialized blueprints** and **33 relational database tables**. It provides multi-role access control tailored for everyday health seekers, certified fitness professionals, and system administrators. Key capabilities include automated Body Mass Index (BMI) categorization, AI-driven goal timelines, step recommendations, water intake tracking with streaks, progress photo galleries, Razorpay payment gateway integration, real-time 1-on-1 coach chat, ReportLab PDF report generation, and an administrative control center.

The primary objective of the project is to eliminate information overload, provide accurate fitness goal predictions, enable direct coach-client digital workflows, and deliver instant offline health summaries. The project follows the Software Development Life Cycle (SDLC), covering requirement analysis, system architecture design, modular blueprint implementation, unit/integration testing, and deployment.

The developed system significantly improves the accessibility, accuracy, and engagement of fitness management while empowering fitness freelancers with a commercial SaaS workspace.

**Keywords:** GoalFit AI Pro, Personalised Fitness, Rule-Based AI, Coach Marketplace, SaaS Dashboard, Razorpay Payment Gateway, SDLC, Web Application.

---

<br>

# TABLE OF CONTENTS (Page vi & vii)

| Chapter / Section                            | Title                                             | Page No. |
| :------------------------------------------- | :------------------------------------------------ | :------: |
| **Title Page**                               |                                                   |    i     |
| **Certificate**                              |                                                   |    ii    |
| **Student Declaration**                      |                                                   |   iii    |
| **Acknowledgement**                          |                                                   |    iv    |
| **Abstract**                                 |                                                   |    v     |
| **Table of Contents**                        |                                                   |    vi    |
| **List of Figures**                          |                                                   |   viii   |
| **List of Tables**                           |                                                   |    ix    |
| **List of Abbreviations**                    |                                                   |    x     |
| **Chapter 1: Introduction**                  |                                                   |  **1**   |
|                                              | 1.1 Background                                    |    1     |
|                                              | 1.2 Problem Statement                             |    2     |
|                                              | 1.3 Objectives of the Project                     |    3     |
|                                              | 1.4 Scope of the Project                          |    4     |
|                                              | 1.5 Organization of the Report                    |    5     |
| **Chapter 2: Literature Review**             |                                                   |  **6**   |
|                                              | 2.1 Existing Systems                              |    6     |
|                                              | 2.2 Comparative Analysis                          |    7     |
|                                              | 2.3 Summary                                       |    8     |
| **Chapter 3: System Requirement Analysis**   |                                                   |  **9**   |
|                                              | 3.1 Functional Requirements                       |    9     |
|                                              | 3.2 Non-Functional Requirements                   |    10    |
|                                              | 3.3 Hardware Requirements                         |    11    |
|                                              | 3.4 Software Requirements                         |    11    |
|                                              | 3.5 Feasibility Study                             |    12    |
|                                              | 3.5.1 Technical Feasibility                       |    12    |
|                                              | 3.5.2 Economic Feasibility                        |    12    |
|                                              | 3.5.3 Operational Feasibility                     |    13    |
| **Chapter 4: System Design and Methodology** |                                                   |  **14**  |
|                                              | 4.1 System Architecture                           |    14    |
|                                              | 4.2 Data Flow Diagrams _(Overview Note)_          |    16    |
|                                              | 4.3 Entity-Relationship Diagram _(Overview Note)_ |    17    |
|                                              | 4.4 Database Design                               |    18    |
|                                              | 4.5 UML Diagrams _(Overview Note)_                |    22    |
| **Chapter 5: Implementation and Coding**     |                                                   |  **24**  |
|                                              | 5.1 Development Environment                       |    24    |
|                                              | 5.2 Module Description                            |    25    |
|                                              | 5.3 Coding Standards                              |    27    |
|                                              | 5.4 Sample Code Snippets                          |    28    |
| **Chapter 6: Testing and Results Analysis**  |                                                   |  **30**  |
|                                              | 6.1 Testing Objectives                            |    30    |
|                                              | 6.2 Testing Methods                               |    30    |
|                                              | 6.3 Test Cases                                    |    31    |
|                                              | 6.4 Results Analysis                              |    34    |
| **Chapter 7: Conclusion and Future Scope**   |                                                   |  **35**  |
|                                              | 7.1 Conclusion                                    |    35    |
|                                              | 7.2 Future Scope                                  |    36    |
| **Bibliography & References**                |                                                   |  **37**  |
| **Appendices**                               |                                                   |  **38**  |
| **Publication / Patent / Research Output**   |                                                   |  **40**  |

---

<br>

# LIST OF FIGURES (Page viii)

|   Figure No.   | Title                                                    | Page No. |
| :------------: | :------------------------------------------------------- | :------: |
| **Figure 4.1** | System Architecture Diagram of GoalFit AI Pro            |    15    |
| **Figure 4.2** | Data Flow Diagram (Level 0 - Context Diagram)            |    16    |
| **Figure 4.3** | Data Flow Diagram (Level 1 - Core Process Decomposition) |    16    |
| **Figure 4.4** | Entity-Relationship (ER) Diagram                         |    17    |
| **Figure 4.5** | Use Case Diagram                                         |    22    |
| **Figure 4.6** | Class Diagram                                            |    23    |
| **Figure 4.7** | Sequence Diagram — Professional Hiring & Payment Process |    23    |
| **Figure 5.1** | User Dashboard & AI Health Plan Interface                |    27    |
| **Figure 5.2** | Professional Marketplace & Hire Flow Interface           |    28    |
| **Figure 5.3** | Professional SaaS Portal (Pro Portal) Interface          |    29    |
| **Figure 6.1** | Test Case Execution Pass/Fail Distribution Graph         |    34    |

---

<br>

# LIST OF TABLES (Page ix)

|   Table No.   | Title                                                           | Page No. |
| :-----------: | :-------------------------------------------------------------- | :------: |
| **Table 2.1** | Comparative Feature Matrix (Existing Systems vs GoalFit AI Pro) |    7     |
| **Table 3.1** | Functional Requirements Specification                           |    10    |
| **Table 3.2** | Hardware Requirements (Server & Client Side)                    |    11    |
| **Table 3.3** | Software Requirements (Server, Client & Dev Tools)              |    11    |
| **Table 4.1** | Database Table Schema — `users`                                 |    18    |
| **Table 4.2** | Database Table Schema — `user_health`                           |    18    |
| **Table 4.3** | Database Table Schema — `bmi_records`                           |    19    |
| **Table 4.4** | Database Table Schema — `professionals`                         |    19    |
| **Table 4.5** | Database Table Schema — `hire_requests`                         |    20    |
| **Table 4.6** | Database Table Schema — `payments`                              |    20    |
| **Table 4.7** | Database Table Schema — `client_assignments`                    |    21    |
| **Table 4.8** | Database Table Schema — `water_logs`                            |    21    |
| **Table 6.1** | Test Cases for Authentication & Health Profile Module           |    31    |
| **Table 6.2** | Test Cases for Marketplace & Razorpay Payment Module            |    32    |
| **Table 6.3** | Test Cases for Professional SaaS Plan Builder Module            |    33    |

---

<br>

# LIST OF ABBREVIATIONS (Page x)

| Abbreviation   | Full Form                          |
| :------------- | :--------------------------------- |
| **SDLC**       | Software Development Life Cycle    |
| **DFD**        | Data Flow Diagram                  |
| **ER Diagram** | Entity-Relationship Diagram        |
| **UML**        | Unified Modeling Language          |
| **GUI**        | Graphical User Interface           |
| **SQL**        | Structured Query Language          |
| **IDE**        | Integrated Development Environment |
| **OS**         | Operating System                   |
| **RAM**        | Random Access Memory               |
| **UI / UX**    | User Interface / User Experience   |
| **CRUD**       | Create, Read, Update, Delete       |
| **BMI**        | Body Mass Index                    |
| **BMR**        | Basal Metabolic Rate               |
| **AJAX**       | Asynchronous JavaScript and XML    |
| **API**        | Application Programming Interface  |
| **SaaS**       | Software as a Service              |
| **WSGI**       | Web Server Gateway Interface       |
| **PDF**        | Portable Document Format           |

---

<br>

# CHAPTER 1: INTRODUCTION

## 1.1 Background

Maintaining a healthy lifestyle through proper nutrition, targeted exercise routines, and consistent health tracking is essential for modern well-being. However, lifestyle-related health disorders such as obesity, malnutrition, hypertension, and sedentary habits are rapidly increasing. Traditionally, individuals seeking to improve their fitness relied on physical gym memberships, manual paper logs, or generic online articles. These manual and fragmented approaches are often time-consuming, prone to human error, unpersonalized, and difficult to maintain over extended periods.

With rapid advancements in information technology and web development, computerizing and automating personalized health management has become both practical and necessary. **GoalFit AI Pro** is an intelligent, full-stack web platform designed to automate diet and exercise planning, calculate health metrics, track hydration and weight progress, and connect users directly with certified personal trainers and dieticians through a digital marketplace.

## 1.2 Problem Statement

Existing fitness tracking systems and mobile applications suffer from several major drawbacks:

1. **Lack of Personalization:** Generic tools provide static, one-size-fits-all diet and workout plans that do not adapt to individual metrics like age, weight, BMI, activity level, or dietary choices (Veg, Non-Veg, Vegan).
2. **Information Overload:** Users are overwhelmed by conflicting online fitness advice without a single, structured system to guide them.
3. **No Intelligent Goal Prediction:** Free platforms fail to estimate realistic timelines (weeks to goal and target completion dates) based on healthy weight change rates.
4. **Fragmented Health Tools:** Tracking calories, workouts, water intake, progress photos, and coach communication requires multiple separate apps, leading to high user drop-off.
5. **Inaccessible & Un-digitized Coaching:** Offline personal trainers and dieticians are expensive, while independent coaches lack an all-in-one SaaS workspace to build digital meal/exercise libraries and manage clients.
6. **Lack of Administrative Oversight:** Platform owners face difficulty verifying coaches, monitoring user growth, auditing payment commissions, and tracking activity logs.

There is, therefore, an urgent need for a centralized, multi-role platform like **GoalFit AI Pro** that manages health tracking, rule-based AI recommendations, coach-client workflows, and platform analytics efficiently and securely.

## 1.3 Objectives of the Project

- To design and implement a centralized MySQL database (33 tables) storing multi-role user, health, professional, payment, and activity data.
- To automate BMI calculation, health categorization, step target generation, and AI-driven goal prediction.
- To deliver rule-based meal and workout plan generators filtering by diet preference (Veg/Non-Veg/Vegan), goal type, and exercise difficulty.
- To build a verified Professional Marketplace with Razorpay payment gateway integration for 1-on-1 coach hiring.
- To create a dedicated Professional SaaS Portal (Pro Portal) enabling coaches to build custom meal/workout libraries and assign plans to clients.
- To implement real-time interactive tools including AJAX water intake tracking with streaks, progress photo galleries, overlay chat messaging, and ReportLab PDF progress report generation.
- To provide a centralized Admin Control Center for user/professional management, verification auditing, payment commission tracking, and feedback management.

## 1.4 Scope of the Project

The scope of **GoalFit AI Pro** encompasses:

- Full-stack web application development using Python Flask and MySQL.
- Multi-role portal access: Everyday Users, Certified Trainers/Dieticians, and System Administrators.
- Secure authentication with PBKDF2-SHA256 hashing and rate limiting via Flask-Limiter.
- End-to-end commercial workflows: Coach browsing, profile inspection, Razorpay checkout, automated plan assignment, progress photo logging, and PDF report downloads.
- Future scope includes mobile app deployment (React Native), LLM chatbot integration (Gemini API), computer vision pose estimation, and wearable hardware sync.

## 1.5 Organization of the Report

This report is organized into seven chapters:

- **Chapter 1** presents the project background, problem statement, objectives, and scope.
- **Chapter 2** reviews existing fitness applications and provides a comparative analysis.
- **Chapter 3** details system requirements, including functional, non-functional, hardware, software, and feasibility analysis.
- **Chapter 4** describes system design, architecture, database schemas, and UML methodologies.
- **Chapter 5** discusses implementation details, module breakdowns, coding standards, and code snippets.
- **Chapter 6** presents testing objectives, test case suites, and result analysis.
- **Chapter 7** concludes the report and outlines future research directions.

---

<br>

# CHAPTER 2: LITERATURE REVIEW

## 2.1 Existing Systems

Several commercial and open-source fitness management solutions are available, ranging from simple calorie tracking apps (e.g., MyFitnessPal, Lose It!) to wearable-connected ecosystems (e.g., Fitbit, Apple Health) and digital coaching platforms (e.g., HealthifyMe).

- **MyFitnessPal:** Focuses heavily on manual food logging; lacks automated goal prediction timelines and integrated personal trainer marketplaces.
- **HealthifyMe:** Combines diet tracking with human coaching, but restricts AI and coach features behind high subscription fees (₹800–₹2000/month) without providing desktop web portal access for coaches.
- **Fitbit Ecosystem:** Highly accurate for step tracking but dependent on expensive hardware wearables, offering limited diet customization.
- **Generic Gym Management Software:** Handles attendance and billing for physical gyms but lacks member-facing AI nutrition/workout planners.

## 2.2 Comparative Analysis

| Feature / Metric           | Generic Apps |  HealthifyMe  | Basic GoalFit AI |              **GoalFit AI Pro**              |
| :------------------------- | :----------: | :-----------: | :--------------: | :------------------------------------------: |
| **AI Personalization**     |     Low      |    Medium     |      Medium      |         **High (Veg/Non-Veg/Vegan)**         |
| **Goal Timeline Engine**   |      No      |   Paid Only   |       Yes        |       **Yes (Automated Date & Weeks)**       |
| **Coach Marketplace**      |      No      |  Proprietary  |        No        | **Yes (Open Trainer/Dietician Marketplace)** |
| **Razorpay Integration**   |      No      | Subscription  |        No        |        **Yes (Direct Package Hire)**         |
| **Pro SaaS Portal**        |      No      | Internal Only |        No        |    **Yes (Custom Meal & Split Builders)**    |
| **Hydration Streaks**      |    Basic     |     Basic     |      Basic       |    **Yes (AJAX 7-Day History & Streaks)**    |
| **Progress Photo Gallery** |      No      |      No       |        No        |     **Yes (With Coach Sharing Control)**     |
| **Instant PDF Report**     |      No      |      No       |      Basic       |     **Yes (ReportLab Publication PDF)**      |
| **Admin Revenue Control**  |      No      |   Corporate   |      Basic       |         **Yes (Commissions & Logs)**         |

## 2.3 Summary

The literature review confirms that existing solutions operate in silos—either providing manual calorie logging without coaching or offering expensive coaching without open web portals. **GoalFit AI Pro** fills this gap by combining rule-based AI automation with a 15% commission-driven professional marketplace and SaaS portal.

---

<br>

# CHAPTER 3: SYSTEM REQUIREMENT ANALYSIS

## 3.1 Functional Requirements

- **FR-1:** System shall support multi-role registration and login (User, Professional, Admin) with PBKDF2-SHA256 password hashing.
- **FR-2:** System shall capture user health parameters (age, gender, height, weight, target weight, activity, diet preference, goal).
- **FR-3:** System shall calculate BMI, store records in `bmi_records`, and assign health categories.
- **FR-4:** System shall estimate goal weeks and completion dates based on weekly weight change rates.
- **FR-5:** System shall generate AI diet plans (Breakfast, Lunch, Dinner, Snacks) and BMI-aware exercise routines with video links.
- **FR-6:** System shall log daily water intake via AJAX, compute streak counts, and display 7-day visual history.
- **FR-7:** System shall allow weight progression tracking and progress photo uploads with privacy toggles.
- **FR-8:** System shall provide a marketplace listing verified professionals with ratings, bios, pricing plans, and transformation stories.
- **FR-9:** System shall interface with Razorpay API for online checkout and payment validation.
- **FR-10:** System shall provide a Pro Portal (`/pro/dashboard`) for coaches to build custom meal/workout libraries and assign plans to active clients.
- **FR-11:** System shall support 1-on-1 overlay chat messaging between hired coaches and clients.
- **FR-12:** System shall generate downloadable PDF progress reports summarizing health stats, BMI logs, and plans.
- **FR-13:** System shall provide an Admin Panel for user/professional management, verification auditing, payment commission tracking, and feedback handling.

## 3.2 Non-Functional Requirements

- **Usability:** Responsive dark-mode interface (Bootstrap 5, Lucide icons, AOS animations) accessible across mobile, tablet, and desktop devices.
- **Reliability:** MySQL foreign key constraints (`ON DELETE CASCADE`, `ON DELETE SET NULL`) ensure strict relational integrity.
- **Performance:** Page render times under 2.0 seconds; AJAX water/chat updates within 300ms; PDF generation under 3.0s.
- **Security:** Session token validation on protected routes, rate limiting via Flask-Limiter (200 requests/day), parameterized SQL queries preventing SQL Injection.
- **Maintainability:** Modular structure across 27 Flask blueprints; configuration separation via `.env`.

## 3.3 Hardware Requirements

| Component     | Server Side (Deployment)               | Client Side (User / Pro Device)  |
| :------------ | :------------------------------------- | :------------------------------- |
| **Processor** | Intel Core i5 / Ryzen 5 (4 Cores+)     | Dual-Core 1.6 GHz or above       |
| **RAM**       | 4 GB (8 GB Recommended)                | 2 GB or above                    |
| **Storage**   | 20 GB SSD (NVMe Preferred)             | Standard Internal Storage        |
| **Display**   | N/A (Headless Linux Server)            | 1280 × 720 or higher resolution  |
| **Network**   | 100 Mbps Dedicated Internet Connection | 3G / 4G / 5G or Wi-Fi Connection |

## 3.4 Software Requirements

| Component              | Technology / Tool                                 | Version / Details                    |
| :--------------------- | :------------------------------------------------ | :----------------------------------- |
| **Operating System**   | Linux (Ubuntu 20.04/22.04 LTS) / Windows 11       | Deployment Environment               |
| **Backend Language**   | Python                                            | Version 3.12                         |
| **Web Framework**      | Flask                                             | Version 3.x (Blueprint Architecture) |
| **Database**           | MySQL                                             | Version 8.0+                         |
| **Database Connector** | `mysql-connector-python`                          | Version 8.x                          |
| **Security & Hashing** | Werkzeug (`generate_password_hash`)               | PBKDF2-SHA256 Encryption             |
| **Rate Limiter**       | Flask-Limiter                                     | 200 req/day, 50 req/hr               |
| **Payment Gateway**    | Razorpay Python SDK                               | Official Integration                 |
| **PDF Generator**      | ReportLab / FPDF2                                 | Automated PDF Document Builder       |
| **Frontend Stack**     | HTML5, CSS3, Bootstrap 5.3, JavaScript (ES6+)     | Vanilla JS with Fetch API            |
| **Data Visualization** | Chart.js                                          | Version 4.x                          |
| **IDE & Tools**        | Visual Studio Code, Git, Postman, MySQL Workbench | Development & Testing                |

## 3.5 Feasibility Study

### 3.5.1 Technical Feasibility

The chosen technologies (Python, Flask, MySQL, Bootstrap 5, Chart.js, Razorpay) are open-source, well-documented, highly stable, and well within the technical expertise of the development team.

### 3.5.2 Economic Feasibility

GoalFit AI Pro utilizes open-source software libraries, resulting in zero software licensing costs. The commercial monetization model (15% platform commission on coach hiring) ensures sustainable operational revenue exceeding server infrastructure costs.

### 3.5.3 Operational Feasibility

The platform is designed with an intuitive dark-themed user interface requiring zero prior training for users or fitness coaches. Admin workflows streamline verification and financial auditing, making operational feasibility exceptionally high.

---

<br>

# CHAPTER 4: SYSTEM DESIGN AND METHODOLOGY

## 4.1 System Architecture

**GoalFit AI Pro** follows a robust **Three-Tier Architecture**:

1. **Presentation Layer (Client Side):** HTML5, CSS3 (Bootstrap 5 dark theme), JavaScript, and Chart.js rendering interactive views for Users, Professionals, and Admins across desktop and mobile devices.
2. **Application Layer (Business Logic):** Flask Web Server organizing business logic across **27 Blueprints**, handling authentication, rule-based AI diet/workout engines, goal predictions, Razorpay payment processing, chat routing, and PDF generation.
3. **Data Layer (Database):** MySQL 8.0 relational database storing **33 tables** managing users, health metrics, professional profiles, custom plans, transactions, activity logs, and chat histories.

```
+-----------------------------------------------------------------------+
|                       PRESENTATION LAYER                              |
|   User Dashboard  |  Marketplace  |  Pro SaaS Portal  |  Admin Panel  |
|   (HTML5 / CSS3 / Bootstrap 5 / JavaScript ES6 / Chart.js Canvas)     |
+-----------------------------------------------------------------------+
                                   | HTTP / AJAX Requests
                                   v
+-----------------------------------------------------------------------+
|                       APPLICATION LAYER (FLASK WSGI)                  |
|  Auth Blueprint  | Health/BMI Blueprint | Diet/Workout AI Generators  |
|  Pro SaaS Portal | Razorpay Payment Engine | ReportLab PDF Generator  |
+-----------------------------------------------------------------------+
                                   | Parameterized SQL Queries
                                   v
+-----------------------------------------------------------------------+
|                          DATA LAYER (MYSQL 8.0)                       |
|   users | user_health | bmi_records | professionals | hire_requests   |
|   custom_diet_plans | custom_workout_plans | payments | chat_messages |
+-----------------------------------------------------------------------+
```

## 4.2 Data Flow Diagrams _(Overview Note)_

_The Data Flow Diagrams (Context Level 0 and Decomposed Level 1 DFDs) illustrate data movement across external actors (Users, Professionals, Admins, Razorpay API) and internal processes (Authentication, Health Analytics, Marketplace Hiring, Custom Plan Construction, PDF Generation). Graphical DFD diagrams are maintained in the primary design repository._

## 4.3 Entity-Relationship Diagram _(Overview Note)_

_The Entity-Relationship (ER) Diagram models 33 relational entities (e.g., `users`, `user_health`, `professionals`, `hire_requests`, `payments`, `client_assignments`, `custom_diet_plans`, `custom_workout_plans`, `chat_messages`). Primary foreign key relationships enforce 1:1, 1:N, and N:M cardinality constraints._

## 4.4 Database Design

Below are primary table schemas from the GoalFit AI Pro database:

### 4.4.1 `users`

| Field Name   | Data Type    | Constraint                | Description                    |
| :----------- | :----------- | :------------------------ | :----------------------------- |
| `id`         | INT          | PK, AUTO_INCREMENT        | Unique user identifier         |
| `name`       | VARCHAR(100) | NOT NULL                  | Display name                   |
| `email`      | VARCHAR(100) | UNIQUE, NOT NULL          | Login email address            |
| `password`   | VARCHAR(255) | NOT NULL                  | PBKDF2-SHA256 hashed password  |
| `role`       | VARCHAR(20)  | DEFAULT 'user'            | Access role (`user` / `admin`) |
| `created_at` | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | Account creation time          |

### 4.4.2 `user_health`

| Field Name        | Data Type   | Constraint         | Description                             |
| :---------------- | :---------- | :----------------- | :-------------------------------------- |
| `id`              | INT         | PK, AUTO_INCREMENT | Health record identifier                |
| `user_id`         | INT         | FK → `users(id)`   | Reference to user                       |
| `age`             | INT         | NOT NULL           | User age                                |
| `gender`          | VARCHAR(20) | NOT NULL           | Gender                                  |
| `height_cm`       | FLOAT       | NOT NULL           | Height in centimeters                   |
| `weight_kg`       | FLOAT       | NOT NULL           | Current weight in kg                    |
| `target_weight`   | FLOAT       | NOT NULL           | Goal weight in kg                       |
| `activity_level`  | VARCHAR(50) | NOT NULL           | Sedentary / Light / Moderate / Active   |
| `goal_type`       | VARCHAR(50) | NOT NULL           | Weight Loss / Weight Gain / Maintenance |
| `diet_preference` | VARCHAR(50) | NOT NULL           | Vegetarian / Non-Vegetarian / Vegan     |

### 4.4.3 `professionals`

| Field Name         | Data Type    | Constraint                   | Description                       |
| :----------------- | :----------- | :--------------------------- | :-------------------------------- |
| `id`               | INT          | PK, AUTO_INCREMENT           | Professional ID                   |
| `full_name`        | VARCHAR(100) | NOT NULL                     | Coach full name                   |
| `email`            | VARCHAR(100) | UNIQUE, NOT NULL             | Professional login email          |
| `password`         | VARCHAR(255) | NOT NULL                     | Hashed password                   |
| `phone`            | VARCHAR(20)  | NULL                         | Contact number                    |
| `role`             | ENUM         | 'trainer','dietician','both' | Professional specialization       |
| `bio`              | TEXT         | NULL                         | Professional background biography |
| `experience_years` | INT          | DEFAULT 0                    | Years of experience               |
| `specialization`   | VARCHAR(255) | NULL                         | Specific expertise areas          |
| `is_verified`      | BOOLEAN      | DEFAULT FALSE                | Admin verification flag           |
| `rating`           | FLOAT        | DEFAULT 0.0                  | Average client review rating      |

### 4.4.4 `payments`

| Field Name            | Data Type    | Constraint               | Description                   |
| :-------------------- | :----------- | :----------------------- | :---------------------------- |
| `id`                  | INT          | PK, AUTO_INCREMENT       | Payment transaction ID        |
| `user_id`             | INT          | FK → `users(id)`         | Paying client                 |
| `professional_id`     | INT          | FK → `professionals(id)` | Recipient coach               |
| `hire_request_id`     | INT          | FK → `hire_requests(id)` | Associated hire order         |
| `razorpay_payment_id` | VARCHAR(100) | UNIQUE                   | Razorpay payment identifier   |
| `amount`              | FLOAT        | NOT NULL                 | Total paid amount (INR)       |
| `commission_amount`   | FLOAT        | NOT NULL                 | Platform commission (15%)     |
| `professional_amount` | FLOAT        | NOT NULL                 | Net payout to coach (85%)     |
| `payment_status`      | VARCHAR(50)  | DEFAULT 'pending'        | `pending` / `paid` / `failed` |

## 4.5 UML Diagrams _(Overview Note)_

_UML Use Case, Class, Activity, and Sequence Diagrams model system interactions—such as User Registration, Health Profile Setup, Coach Hiring via Razorpay, Pro Plan Assignment, and PDF Exports. Behavioral diagrams are documented in the supplementary architectural specification._

---

<br>

# CHAPTER 5: IMPLEMENTATION AND CODING

## 5.1 Development Environment

**GoalFit AI Pro** was implemented using Visual Studio Code and Python 3.12. Environment configuration uses `python-dotenv` for database host (`DB_HOST`), username (`DB_USER`), password (`DB_PASSWORD`), database name (`goalfit_ai`), and secret keys. Version control was managed via Git repository commits.

## 5.2 Module Description

### 5.2.1 Authentication & Security Module (`auth.py`, `professional_auth.py`)

Handles user and professional registration, login authentication, password hashing (`generate_password_hash`), session management, and first-time login redirection. Protected routes enforce `@login_required`, `@pro_required`, and `@admin_required` decorators.

### 5.2.2 Health Profile & BMI Engine (`health.py`, `bmi.py`, `prediction.py`)

Processes age, height, weight, target weight, activity, and diet preferences. Calculates BMI, logs history in `bmi_records`, estimates goal completion weeks, and computes daily step/calorie targets.

### 5.2.3 AI Diet & Workout Plan Generator (`diet.py`, `workout.py`)

Executes rule-based SQL queries retrieving meals matching diet type (Veg/Non-Veg/Vegan) and goal, and exercises matching user BMI category difficulty level.

### 5.2.4 Water & Progress Tracking Module (`water.py`, `progress.py`, `progress_gallery.py`)

Provides AJAX endpoints for logging water consumption, calculating consecutive streak counts, rendering 7-day hydration graphs, weight progress line charts (Chart.js), and managing progress photo uploads.

### 5.2.5 Marketplace & Payment Module (`marketplace.py`, `payment_gateway.py`)

Renders coach cards, detailed profiles, pricing tiers, and client transformation stories. Integrates Razorpay Python SDK to create order IDs and verify payment webhooks.

### 5.2.6 Professional SaaS Portal (`professional_dashboard.py`, `diet_management.py`, `workout_management.py`)

Empowers trainers/dieticians to build custom meal/workout libraries, assemble client-specific diet/workout plans, review active clients, track earnings (85% net split), and respond to client requests.

### 5.2.7 PDF Report Generator (`report.py`, `pdf_generator.py`)

Uses ReportLab to build multi-page PDF progress reports summarizing user parameters, BMI logs, predictions, step goals, water intake, and assigned diet/workout schedules.

### 5.2.8 Admin Control Center (`admin.py`)

Provides system administrators with platform-wide analytics: Total users, verified coaches, gross revenue, net commissions, user growth charts, coach verification toggles, and feedback inbox management.

## 5.3 Coding Standards

- PEP 8 Python formatting standards.
- Parameterized SQL queries preventing SQL Injection.
- Modular blueprint structure across 27 separate Python module files.
- Reusable Jinja2 template inheritance (`base.html`, `pro_base.html`, `admin_base.html`).

## 5.4 Sample Code Snippets

### Snippet 1: Goal Prediction Engine (`modules/prediction.py`)

```python
def calculate_goal_prediction(current_weight, target_weight, goal_type):
    weight_difference = abs(current_weight - target_weight)

    # Safe weekly weight change rate (kg/week)
    if goal_type == 'Weight Loss':
        weekly_rate = 0.75  # Safe loss rate
    elif goal_type == 'Weight Gain':
        weekly_rate = 0.50  # Safe gain rate
    else:
        weekly_rate = 0.0

    if weekly_rate > 0:
        estimated_weeks = int(round(weight_difference / weekly_rate))
    else:
        estimated_weeks = 0

    completion_date = datetime.now() + timedelta(weeks=estimated_weeks)
    return estimated_weeks, completion_date.strftime('%Y-%m-%d')
```

### Snippet 2: Razorpay Payment Verification (`modules/payment_gateway.py`)

```python
@payment_gateway_bp.route('/payment/verify', methods=['POST'])
def verify_payment():
    data = request.json
    params_dict = {
        'razorpay_order_id': data['razorpay_order_id'],
        'razorpay_payment_id': data['razorpay_payment_id'],
        'razorpay_signature': data['razorpay_signature']
    }

    try:
        # Verify Razorpay signature
        client.utility.verify_payment_signature(params_dict)

        # Calculate platform revenue commission (15%)
        amount = float(data['amount'])
        commission = amount * 0.15
        pro_amount = amount - commission

        # Insert payment & activate hire request in database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO payments (user_id, professional_id, hire_request_id, razorpay_payment_id, amount, commission_amount, professional_amount, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'paid')
        """, (session['user_id'], data['pro_id'], data['hire_id'], data['razorpay_payment_id'], amount, commission, pro_amount))

        cursor.execute("UPDATE hire_requests SET status='accepted', payment_status='paid' WHERE id=%s", (data['hire_id'],))
        conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
```

---

<br>

# CHAPTER 6: TESTING AND RESULTS ANALYSIS

## 6.1 Testing Objectives

To verify that all GoalFit AI Pro modules operate correctly, securely, and seamlessly across multi-role workflows (User, Professional, Admin), ensuring data integrity, payment validation, and UI responsiveness.

## 6.2 Testing Methods

1. **Unit Testing:** Validated independent functions (BMI calculation, goal prediction date, password hashing, 15% commission splitting).
2. **Integration Testing:** Verified multi-step workflows (User Signup → Health Profile → AI Plan Generation; Marketplace Browse → Razorpay Payment → Pro Client Assignment).
3. **User Acceptance Testing (UAT):** Conducted testing with sample users and fitness coaches to validate real-world usability.

## 6.3 Test Cases

### 6.3.1 Authentication & Health Profile Module

| Test Case ID | Description                       | Expected Result                                       |  Status  |
| :----------: | :-------------------------------- | :---------------------------------------------------- | :------: |
|  **TC-01**   | Register user with new email      | Account created, password hashed, redirect to login   | **PASS** |
|  **TC-02**   | Register user with existing email | Error message displayed ("Email already registered")  | **PASS** |
|  **TC-03**   | First-time user login             | Session created, forced redirect to `/health/profile` | **PASS** |
|  **TC-04**   | Save health profile (75kg, 175cm) | BMI calculated (24.49 - Normal), predictions saved    | **PASS** |

### 6.3.2 Marketplace & Razorpay Payment Module

| Test Case ID | Description                        | Expected Result                                              |  Status  |
| :----------: | :--------------------------------- | :----------------------------------------------------------- | :------: |
|  **TC-05**   | Browse marketplace coaches         | Verified trainers/dieticians rendered with ratings & pricing | **PASS** |
|  **TC-06**   | Initiate Razorpay checkout         | Order ID generated server-side, Razorpay modal opens         | **PASS** |
|  **TC-07**   | Valid payment signature submission | Payment logged, 15% commission computed, status = `paid`     | **PASS** |
|  **TC-08**   | Invalid payment signature          | Exception caught, transaction rejected                       | **PASS** |

### 6.3.3 Professional SaaS & PDF Module

| Test Case ID | Description                   | Expected Result                                      |  Status  |
| :----------: | :---------------------------- | :--------------------------------------------------- | :------: |
|  **TC-09**   | Pro coach creates custom meal | Meal added to `professional_meals` library           | **PASS** |
|  **TC-10**   | Assign custom plan to client  | Client dashboard updates with coach's custom plan    | **PASS** |
|  **TC-11**   | Click "Download PDF Report"   | Publication-quality PDF generated & downloaded (<3s) | **PASS** |

## 6.4 Results Analysis

All test cases across authentication, health analytics, marketplace hiring, Razorpay payments, Pro SaaS management, and PDF generation produced expected results (**100% Pass Rate**).

```
+-------------------------------------------------------------+
|               TEST EXECUTION RESULTS ANALYSIS               |
|                                                             |
|   [=========================================] 100% PASS     |
|                                                             |
|   Total Test Cases Executed : 11                            |
|   Passed Test Cases         : 11 (100%)                     |
|   Failed Test Cases         : 0  (0%)                       |
+-------------------------------------------------------------+
```

---

<br>

# CHAPTER 7: CONCLUSION AND FUTURE SCOPE

## 7.1 Conclusion

**GoalFit AI Pro** successfully modernizes and integrates personalized health management, rule-based AI fitness planning, and professional digital coaching into a single, scalable web platform. By combining automated BMI categorization, goal timeline predictions, AJAX water tracking, progress photo galleries, a verified coach marketplace, Razorpay payment processing, and a dedicated Pro SaaS Portal, the system addresses the major limitations of existing generic or expensive fitness tools. Testing confirmed that the system fulfills all functional, non-functional, security, and financial requirements.

## 7.2 Future Scope

- **LLM-Powered Conversational Coach:** Integrating Google Gemini Pro API for 24/7 conversational diet and workout Q&A.
- **Computer Vision Pose Correction:** Implementing MediaPipe/TensorFlow.js webcam pose analysis for real-time exercise form correction.
- **AI Calorie Estimation from Food Photos:** Computer vision food recognition automatically logging macros from meal pictures.
- **Wearable Device Integration:** Automatic synchronization with Apple HealthKit, Google Fit, and Smartwatches.
- **Native Cross-Platform Mobile Apps:** Deploying React Native / Flutter apps with native push notifications.

---

<br>

# BIBLIOGRAPHY & REFERENCES

1. **Flask Documentation:** Pallets Projects. _Flask WSGI Web Framework Documentation (v3.x)_. Available at: https://flask.palletsprojects.com/
2. **MySQL Reference Manual:** Oracle Corporation. _MySQL 8.0 Reference Manual_. Available at: https://dev.mysql.com/doc/refman/8.0/en/
3. **Bootstrap 5 Framework:** Twitter / Bootstrap Core Team. _Bootstrap v5.3 Design Guidelines_. Available at: https://getbootstrap.com/docs/5.3/
4. **Chart.js Library:** Chart.js Open Source Team. _Chart.js Interactive Visualization Docs_. Available at: https://www.chartjs.org/docs/latest/
5. **Razorpay Developer API:** Razorpay Software Pvt. Ltd. _Razorpay Payment Gateway API Docs_. Available at: https://razorpay.com/docs/
6. **ReportLab Toolkit:** ReportLab Europe Ltd. _ReportLab PDF Generation Guide_. Available at: https://www.reportlab.com/documentation/
7. **Werkzeug Utilities:** Pallets Projects. _Werkzeug Security & Password Hashing_. Available at: https://werkzeug.palletsprojects.com/
8. **Flask-Limiter Extension:** Limit-Extension Community. _Flask-Limiter Rate Limiting Docs_. Available at: https://flask-limiter.readthedocs.io/
9. **World Health Organization (WHO):** _Physical Activity and Global Health Guidelines (2022)_. Available at: https://www.who.int/news-room/fact-sheets/detail/physical-activity
10. **Harvard Health Publishing:** _Dietary Guidelines & Weight Loss Science_. Harvard Medical School. Available at: https://www.health.harvard.edu/topics/diet-and-weight-loss

---

<br>

# APPENDICES

### Appendix A: Review 1 — Scanned Copy

_[Insert scanned copy of signed Review 1 evaluation sheet here]_

### Appendix B: Review 2 — Scanned Copy

_[Insert scanned copy of signed Review 2 evaluation sheet here]_

### Appendix C: Review 3 — Scanned Copy

_[Insert scanned copy of signed Review 3 evaluation sheet here]_

### Appendix D: Review 4 — Scanned Copy

_[Insert scanned copy of signed Review 4 evaluation sheet here]_

---

<br>

# PUBLICATION / PATENT / RESEARCH OUTPUT

_(This section is optional and applicable if students publish a research paper or file a patent based on this project.)_

_[Insert scanned copy of publication acceptance letter / patent filing receipt here if applicable]_
