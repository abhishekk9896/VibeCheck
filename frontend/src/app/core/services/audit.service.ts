import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuditSession, CreateAuditRequest } from '../models/audit.model';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuditService {
  private apiUrl = 'http://127.0.0.1:8000/audits';

  constructor(private http: HttpClient, private authService: AuthService) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      Authorization: `Bearer ${token}`
    });
  }

  createAudit(data: CreateAuditRequest): Observable<AuditSession> {
    return this.http.post<AuditSession>(this.apiUrl, data, { headers: this.getHeaders() });
  }

  getAudits(): Observable<AuditSession[]> {
    return this.http.get<AuditSession[]>(this.apiUrl, { headers: this.getHeaders() });
  }

  getAuditById(id: number): Observable<AuditSession> {
    return this.http.get<AuditSession>(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }
}