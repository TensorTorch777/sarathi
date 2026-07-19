import { AuthForm } from "@/components/auth/AuthForm";
import { GuestOnly } from "@/components/auth/GuestOnly";

export default function RegisterPage() {
  return (
    <GuestOnly>
      <AuthForm mode="register" />
    </GuestOnly>
  );
}
