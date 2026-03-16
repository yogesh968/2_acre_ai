import axios, { AxiosInstance } from 'axios';
import { Patient, Appointment, Doctor, AvailabilitySlot } from '@/types';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Patients
  async createPatient(data: Partial<Patient>): Promise<Patient> {
    const response = await this.client.post('/patients', data);
    return response.data;
  }

  async getPatient(id: string): Promise<Patient> {
    const response = await this.client.get(`/patients/${id}`);
    return response.data;
  }

  // Appointments
  async createAppointment(data: Partial<Appointment>): Promise<Appointment> {
    const response = await this.client.post('/appointments', data);
    return response.data;
  }

  async getAppointment(id: string): Promise<Appointment> {
    const response = await this.client.get(`/appointments/${id}`);
    return response.data;
  }

  async updateAppointment(id: string, data: Partial<Appointment>): Promise<Appointment> {
    const response = await this.client.put(`/appointments/${id}`, data);
    return response.data;
  }

  async cancelAppointment(id: string): Promise<void> {
    await this.client.delete(`/appointments/${id}`);
  }

  async getPatientAppointments(patientId: string): Promise<Appointment[]> {
    const response = await this.client.get(`/patients/${patientId}/appointments`);
    return response.data;
  }

  // Doctors
  async getDoctors(): Promise<Doctor[]> {
    const response = await this.client.get('/doctors');
    return response.data;
  }

  async getDoctor(id: string): Promise<Doctor> {
    const response = await this.client.get(`/doctors/${id}`);
    return response.data;
  }

  async getDoctorAvailability(
    doctorId: string,
    startDate: string,
    endDate: string
  ): Promise<AvailabilitySlot[]> {
    const response = await this.client.get('/doctors/availability', {
      params: { doctor_id: doctorId, start_date: startDate, end_date: endDate },
    });
    return response.data;
  }
}

export const apiService = new ApiService();
