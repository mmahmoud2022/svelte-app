import api from './api';

// =============== Type Definitions ===============

export type Specialty = 
  | 'general_practitioner'
  | 'cardiologist'
  | 'dermatologist'
  | 'pediatrician'
  | 'gynecologist'
  | 'psychiatrist'
  | 'ophthalmologist'
  | 'dentist'
  | 'orthopedist'
  | 'neurologist'
  | 'radiologist'
  | 'surgeon'
  | 'other';

export type ConsultationType = 
  | 'in_person'
  | 'teleconsultation'
  | 'both';

export type AppointmentStatus = 
  | 'pending'
  | 'confirmed'
  | 'cancelled'
  | 'completed'
  | 'no_show';

export type PaymentStatus = 
  | 'pending'
  | 'completed'
  | 'failed'
  | 'refunded';

export interface DoctorProfile {
  id: number;
  user_id: number;
  specialty: Specialty;
  sub_specialty?: string;
  rpps_number?: string; // Optional
  office_address?: string;
  office_city?: string;
  office_postal_code?: string;
  office_phone?: string;
  biography?: string;
  languages?: string[];
  education?: any[];
  experience_years: number;
  consultation_types: ConsultationType;
  consultation_duration: number;
  consultation_price?: number;
  accepts_new_patients: boolean;
  is_public: boolean;
  is_verified: boolean;
  total_consultations: number;
  average_rating: number;
  total_reviews: number;
  created_at: string;
  updated_at?: string;
  // User info
  first_name?: string;
  last_name?: string;
  email?: string;
  user?: {
    id: number;
    email: string;
    full_name: string;
    phone?: string;
  };
}

export interface DoctorAvailability {
  id: number;
  doctor_id: number;
  day_of_week: number;
  start_time: string;
  end_time: string;
  consultation_type: ConsultationType;
  is_available: boolean;
  created_at: string;
}

export interface Appointment {
  id: number;
  doctor_id: number;
  patient_id: number;
  appointment_date: string;
  consultation_type: ConsultationType;
  status: AppointmentStatus;
  reason?: string;
  patient_notes?: string;
  doctor_notes?: string;
  notes?: string;
  prescription?: string;
  diagnosis?: string;
  created_at: string;
  updated_at: string;
  doctor?: DoctorProfile;
  patient?: {
    id: number;
    email: string;
    full_name: string;
    phone?: string;
  };
}

export interface DoctorReview {
  id: number;
  doctor_id: number;
  patient_id: number;
  appointment_id?: number;
  rating: number;
  comment?: string;
  created_at: string;
  patient?: {
    id: number;
    full_name: string;
  };
}

export interface DoctorMessage {
  id: number;
  sender_id: number;
  receiver_id: number;
  appointment_id?: number;
  message: string;
  is_read: boolean;
  created_at: string;
  sender?: {
    id: number;
    full_name: string;
  };
  receiver?: {
    id: number;
    full_name: string;
  };
}

export interface Payment {
  id: number;
  doctor_id: number;
  patient_id: number;
  appointment_id?: number;
  amount: number;
  currency: string;
  status: PaymentStatus;
  payment_method?: string;
  transaction_id?: string;
  created_at: string;
  paid_at?: string;
  refunded_at?: string;
}

export interface PatientDocument {
  id: number;
  patient_id: number;
  doctor_id?: number;
  appointment_id?: number;
  document_type: string;
  file_path: string;
  file_name: string;
  description?: string;
  uploaded_at: string;
}

export interface DoctorSettings {
  id: number;
  doctor_id: number;
  notifications_enabled: boolean;
  email_notifications: boolean;
  sms_notifications: boolean;
  auto_confirm_appointments: boolean;
  booking_buffer_minutes: number;
  max_appointments_per_day?: number;
  created_at: string;
  updated_at: string;
}

export interface DoctorStatistics {
  total_appointments: number;
  completed_appointments: number;
  cancelled_appointments: number;
  pending_appointments: number;
  total_patients: number;
  average_rating: number;
  total_reviews: number;
  total_revenue: number;
  appointments_this_month: number;
  revenue_this_month: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// =============== Create/Update Schemas ===============

export interface DoctorProfileCreate {
  specialty: Specialty;
  rpps_number?: string; // Optional: 11-digit RPPS number
  sub_specialty?: string;
  office_address?: string;
  office_city?: string;
  office_postal_code?: string;
  office_phone?: string;
  biography?: string;
  languages?: string[];
  education?: any[];
  experience_years?: number;
  consultation_types?: ConsultationType;
  consultation_duration?: number;
  consultation_price?: number;
  accepts_new_patients?: boolean;
  is_public?: boolean;
}

export interface DoctorProfileUpdate {
  specialty?: Specialty;
  rpps_number?: string; // Optional: 11-digit RPPS number
  sub_specialty?: string;
  office_address?: string;
  office_city?: string;
  office_postal_code?: string;
  office_phone?: string;
  biography?: string;
  languages?: string[];
  education?: any[];
  experience_years?: number;
  consultation_types?: ConsultationType;
  consultation_duration?: number;
  consultation_price?: number;
  accepts_new_patients?: boolean;
  is_public?: boolean;
}

export interface AvailabilityCreate {
  day_of_week: number;
  start_time: string;
  end_time: string;
  consultation_type: ConsultationType;
  is_available?: boolean;
}

export interface AppointmentCreate {
  patient_id: number;
  appointment_date: string;
  consultation_type: ConsultationType;
  reason?: string;
}

export interface AppointmentStatusUpdate {
  status: AppointmentStatus;
  notes?: string;
  prescription?: string;
  diagnosis?: string;
}

export interface ReviewCreate {
  doctor_id: number;
  appointment_id?: number;
  rating: number;
  comment?: string;
}

export interface MessageCreate {
  receiver_id: number;
  appointment_id?: number;
  message: string;
}

// =============== API Functions ===============

// Profile Management
export const createDoctorProfile = async (data: DoctorProfileCreate): Promise<DoctorProfile> => {
  const response = await api.post<DoctorProfile>('/api/v1/doctors/', data);
  return response.data;
};

export const getCurrentDoctorProfile = async (): Promise<DoctorProfile> => {
  const response = await api.get<DoctorProfile>('/api/v1/doctors/me');
  return response.data;
};

export const updateDoctorProfile = async (data: DoctorProfileUpdate): Promise<DoctorProfile> => {
  const response = await api.put<DoctorProfile>('/api/v1/doctors/me', data);
  return response.data;
};

export const getDoctorProfile = async (doctorId: number): Promise<DoctorProfile> => {
  const response = await api.get<DoctorProfile>(`/api/v1/doctors/${doctorId}`);
  return response.data;
};

// Availability Management
export const createAvailability = async (data: AvailabilityCreate): Promise<DoctorAvailability> => {
  const response = await api.post<DoctorAvailability>('/api/v1/doctors/availability', data);
  return response.data;
};

export const getDoctorAvailability = async (doctorId: number): Promise<DoctorAvailability[]> => {
  const response = await api.get<DoctorAvailability[]>(`/api/v1/doctors/${doctorId}/availability`);
  return response.data;
};

export const deleteAvailability = async (availabilityId: number): Promise<void> => {
  await api.delete(`/api/v1/doctors/availability/${availabilityId}`);
};

// Appointment Management
export const createAppointment = async (data: AppointmentCreate): Promise<Appointment> => {
  const response = await api.post<Appointment>('/api/v1/doctors/appointments', data);
  return response.data;
};

export const getDoctorAppointments = async (
  page: number = 1,
  pageSize: number = 10,
  status?: AppointmentStatus
): Promise<PaginatedResponse<Appointment>> => {
  const params: any = { page, page_size: pageSize };
  if (status) params.status_filter = status;
  const response = await api.get<PaginatedResponse<Appointment>>('/api/v1/doctors/appointments', { params });
  return response.data;
};

export const getAppointmentById = async (appointmentId: number): Promise<Appointment> => {
  const response = await api.get<Appointment>(`/api/v1/doctors/appointments/${appointmentId}`);
  return response.data;
};

export const updateAppointmentStatus = async (
  appointmentId: number,
  data: AppointmentStatusUpdate
): Promise<Appointment> => {
  const response = await api.patch<Appointment>(
    `/api/v1/doctors/appointments/${appointmentId}/status`,
    data
  );
  return response.data;
};

export const getPatientAppointments = async (patientId: number): Promise<Appointment[]> => {
  const response = await api.get<Appointment[]>(`/api/v1/doctors/patients/${patientId}/appointments`);
  return response.data;
};

// Reviews Management
export const getDoctorReviews = async (
  doctorId: number,
  page: number = 1,
  page_size: number = 10
): Promise<PaginatedResponse<DoctorReview>> => {
  const response = await api.get<PaginatedResponse<DoctorReview>>(
    `/api/v1/doctors/${doctorId}/reviews`,
    { params: { page, page_size } }
  );
  return response.data;
};

export const getMyReviews = async (
  page: number = 1,
  page_size: number = 10
): Promise<PaginatedResponse<DoctorReview>> => {
  const response = await api.get<PaginatedResponse<DoctorReview>>(
    '/api/v1/doctors/reviews',
    { params: { page, page_size } }
  );
  return response.data;
};

export const respondToReview = async (
  reviewId: number,
  response: string
): Promise<DoctorReview> => {
  const result = await api.post<DoctorReview>(
    `/api/v1/doctors/reviews/${reviewId}/respond`,
    { response }
  );
  return result.data;
};

// Messaging
export const sendMessage = async (data: MessageCreate): Promise<DoctorMessage> => {
  const response = await api.post<DoctorMessage>('/api/v1/doctors/messages', data);
  return response.data;
};

export const getDoctorMessages = async (
  page: number = 1,
  page_size: number = 50
): Promise<PaginatedResponse<DoctorMessage>> => {
  const response = await api.get<PaginatedResponse<DoctorMessage>>('/api/v1/doctors/messages', {
    params: { page, page_size }
  });
  return response.data;
};

// Payments
export const getDoctorPayments = async (
  page: number = 1,
  page_size: number = 10,
  status?: PaymentStatus
): Promise<PaginatedResponse<Payment>> => {
  const params: any = { page, page_size };
  if (status) params.status = status;
  const response = await api.get<PaginatedResponse<Payment>>('/api/v1/doctors/payments', { params });
  return response.data;
};

// Documents
export const getDocument = async (documentId: number): Promise<PatientDocument> => {
  const response = await api.get<PatientDocument>(`/api/v1/doctors/documents/${documentId}`);
  return response.data;
};

// Statistics
export const getDoctorStatistics = async (): Promise<DoctorStatistics> => {
  const response = await api.get<DoctorStatistics>('/api/v1/doctors/statistics');
  return response.data;
};

// Patients Management
export interface PatientInfo {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  date_of_birth?: string;
  total_appointments: number;
  last_appointment_date?: string;
}

export const getMyPatients = async (
  page: number = 1,
  page_size: number = 50
): Promise<PaginatedResponse<PatientInfo>> => {
  const response = await api.get<PaginatedResponse<PatientInfo>>(
    '/api/v1/doctors/patients',
    { params: { page, page_size } }
  );
  return response.data;
};

export interface MedicalRecord {
  patient: any;
  appointments: Appointment[];
  documents: PatientDocument[];
  total_consultations: number;
}

export const getPatientMedicalRecord = async (patientId: number): Promise<MedicalRecord> => {
  const response = await api.get<MedicalRecord>(`/api/v1/doctors/patients/${patientId}`);
  return response.data;
};

// Settings Management
export const getMySettings = async (): Promise<DoctorSettings> => {
  const response = await api.get<DoctorSettings>('/api/v1/doctors/settings');
  return response.data;
};

export const updateMySettings = async (data: Partial<DoctorSettings>): Promise<DoctorSettings> => {
  const response = await api.put<DoctorSettings>('/api/v1/doctors/settings', data);
  return response.data;
};

export default {
  // Profile
  createDoctorProfile,
  getCurrentDoctorProfile,
  updateDoctorProfile,
  getDoctorProfile,
  
  // Availability
  createAvailability,
  getDoctorAvailability,
  deleteAvailability,
  
  // Appointments
  createAppointment,
  getDoctorAppointments,
  getAppointmentById,
  updateAppointmentStatus,
  getPatientAppointments,
  
  // Reviews
  getDoctorReviews,
  getMyReviews,
  respondToReview,
  
  // Messaging
  sendMessage,
  getDoctorMessages,
  
  // Payments
  getDoctorPayments,
  
  // Documents
  getDocument,
  
  // Statistics
  getDoctorStatistics,
  
  // Patients
  getMyPatients,
  getPatientMedicalRecord,
  
  // Settings
  getMySettings,
  updateMySettings,
};
