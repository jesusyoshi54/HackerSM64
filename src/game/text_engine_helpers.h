s32 TE_inc_state(s32 *state);
s32 TE_dec_state(s32 *state);
s32 TE_mod_state(s32 *state, s32 mod);
s32 TE_get_state(s32 *state);
s32 TE_get_flag(s32 *flag,u32 bit);
s32 TE_set_flag(s32 *flag,u32 bit);
s32 TE_check_password(char *password,u32 usr);
s32 TE_set_state(s32 *state,u32 value);
void TE_print_star_cnt(s32 fileindex, s32 usr, u8 eng);